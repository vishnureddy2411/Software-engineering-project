import calendar
from datetime import date, datetime
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Slot, Booking
from sports.models import Location, Sport
from bookings.models import Slot, Booking
from bookings.forms import SlotForm
from .utils import AvailabilityHTMLCalendar
from accounts.models import User, Admin
from django.utils.timezone import now
import logging
from django.db import connection, IntegrityError

from django.utils import timezone 

from bookings.forms import SlotForm, BookingAdminForm, BookingAdminUpdateForm

from django.http import JsonResponse



logger = logging.getLogger(__name__)
@login_required
def choose_location(request):
    locations = Location.objects.all().order_by('name')
    if request.method == "POST":
        location_id = request.POST.get("location")
        if location_id:
            logger.info("Location %s selected by user %s", location_id, request.user.username)
            return redirect("choose_sport", location_id=location_id)
        messages.error(request, "Please select a location.")
    return render(request, "choose_location.html", {"locations": locations})
@login_required
def choose_sport(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    sports = Sport.objects.filter(location=location)

    if request.method == "POST":
        sport_id = request.POST.get("sport")
        sport = get_object_or_404(Sport, sport_id=sport_id)

        if sport_id:
            logger.info("Sport %s chosen at location %s by user %s", sport_id, location.name, request.user.username)

            current_time = datetime.now().time()  # Use server's current time in the right timezone
            current_price = sport.get_current_price(current_time)

            return render(request, sport.name + ".html", {
                "location": location,
                "sport": sport,
                "price": current_price,
                "address": location.address,
                "is_peak": current_price == sport.peak_price and sport.peak_price is not None,
                "normal_price": sport.price,
                "peak_price": sport.peak_price
            })

        messages.error(request, "Please select a sport.")

    return render(request, "choose_sport.html", {"location": location, "sports": sports})


class AvailabilityHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, availability, location_id, sport_id):
        super().__init__()
        self.availability = availability
        self.location_id = location_id
        self.sport_id = sport_id

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        day_str = f"{self.year}-{self.month:02d}-{day:02d}"
        if self.availability.get(day_str):
            return (
                f'<td class="available" data-date="{day_str}">'
                f'<a href="/bookings/slots/{self.location_id}/{self.sport_id}/{day_str}/">{day}</a>'
                f'</td>'
            )
        return f'<td class="unavailable">{day}</td>'

    def formatmonth(self, theyear, themonth, withyear=True):
        self.year, self.month = theyear, themonth
        return super().formatmonth(theyear, themonth, withyear)


def choose_date(request, location_id, sport_id):
    """Displays a calendar for users to choose a booking date. Only present and future dates are available."""
    location = get_object_or_404(Location, pk=location_id)
    sport = get_object_or_404(Sport, pk=sport_id)
    today = date.today()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))

        # Adjust year and month if they are in the past
        if date(year, month, 1) < date(today.year, today.month, 1):
            year, month = today.year, today.month

        if month < 1:
            year -= 1
            month = 12
        elif month > 12:
            year += 1
            month = 1
    except (ValueError, TypeError):
        year, month = today.year, today.month

    availability = {}
    _, num_days = calendar.monthrange(year, month)

    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        if current_date >= today:
            day_str = current_date.strftime("%Y-%m-%d")
            slots_available = Slot.objects.filter(
                date=current_date, location=location, sport=sport, is_booked=False
            ).exists()
            availability[day_str] = slots_available
        else:
            availability[current_date.strftime("%Y-%m-%d")] = False

    logger.info("Availability Data for %d-%02d: %s", year, month, availability)

    cal = AvailabilityHTMLCalendar(availability, location_id, sport_id)
    calendar_html = cal.formatmonth(year, month)

    context = {
        "calendar_html": calendar_html,
        "location": location,
        "sport": sport,
        "year": year,
        "month": month,
    }
    return render(request, "choose_date_calendar.html", context)




def list_slots(request, location_id, sport_id, date):
    """
    Display available slots for a given date, location, and sport.
    Ensures that only slots from the current time onward are displayed for the current day.
    """
    try:
        # Parse and validate the selected date
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Invalid date format. Please try again.")
        return redirect("choose_date", location_id=location_id, sport_id=sport_id)

    location = get_object_or_404(Location, location_id=location_id)
    sport = get_object_or_404(Sport, sport_id=sport_id)

    # Fetch the current time and date
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()

    # Filter slots to exclude past times for today
    if selected_date > current_date:
        # For future dates, show all available slots (no time restriction)
        slots = Slot.objects.filter(
            date=selected_date,
            location=location,
            sport=sport,
            is_booked=False
        )
    elif selected_date == current_date:
        # For the current date, only show slots with time greater than or equal to the current time (e.g., 6:00 PM)
        slots = Slot.objects.filter(
            date=selected_date,
            location=location,
            sport=sport,
            is_booked=False,
            time__gte=current_time  # Exclude past times for today
        )
    else:
        # For past dates, no slots should be displayed
        slots = Slot.objects.none()

    # Redirect if no slots are available
    if not slots.exists():
        messages.info(request, f"No slots available on {selected_date}. Please choose another date.")
        return redirect("choose_date", location_id=location_id, sport_id=sport_id)

    if request.method == "POST":
        slot_id = request.POST.get("slot")
        if slot_id:
            # Redirect to confirm_booking with the selected slot_id
            return redirect("confirm_booking", slot_id=slot_id)
        else:
            messages.error(request, "Please select a slot.")

    context = {
        "slots": slots,
        "date": selected_date,
        "location": location,
        "sport": sport,
        "location_id": location_id,  # Pass location ID explicitly
        "sport_id": sport_id,  # Pass sport ID explicitly
    }
    return render(request, "list_slots.html", context)




@login_required
def confirm_booking(request, slot_id):
    """
    Handles the booking confirmation process, including setting the booking's date
    to match the slot's date.
    """
    # Fetch the slot by slot_id
    slot = get_object_or_404(Slot, pk=slot_id)

    # Retrieve slot date and time
    slot_date = slot.date  # Access the `date` column from the Slot table
    slot_time = slot.time  # Access the `time` column from the Slot table

    # Handle the case if the slot date or time is missing
    if not slot_date or not slot_time:
        messages.error(request, "This slot has incomplete details. Please select another slot.")
        return redirect("choose_date", location_id=slot.location_id, sport_id=slot.sport_id)

    # Handle the case if the slot is already booked
    if slot.is_booked:
        messages.error(request, "This slot is no longer available. Please select another slot.")
        return redirect("choose_date", location_id=slot.location_id, sport_id=slot.sport_id)

    # Process POST request for confirming booking
    if request.method == "POST":
        # Create the booking, ensuring the booking date matches the slot's date
        booking = Booking.objects.create(
            user=request.user,
            sport=slot.sport,
            slot=slot,
            location=slot.location,
            status="Pending",
            time_slot=slot_time,  # Set the booking's time from slot's time
            date=slot_date,       # Set the booking's date from slot's date
        )

        # Mark the slot as booked
        slot.is_booked = True
        slot.save()

        # Redirect to the payment page before finalizing booking
        return redirect("payments_page", booking_id=booking.booking_id)

    # Pass slot details to the template
    context = {
        "slot": slot,  # Slot details
    }

    return render(request, "confirm_booking.html", context)



def booking_success(request):
    # Get the latest booking for the user
    booking = Booking.objects.filter(user=request.user).last()

    # Handle case where no booking exists
    if not booking:
        return render(request, "error.html", {"message": "No booking found!"}) 

    return render(request, "booking_success.html", {"booking": booking})
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    logger.info("User %s accessed their bookings. Total: %d", request.user.username, bookings.count())
    return render(request, "my_bookings.html", {"bookings": bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    logger.info("User %s is viewing details of booking ID %s", request.user.username, booking_id)
    return render(request, "booking_detail.html", {"booking": booking})



logger = logging.getLogger(__name__)

@login_required
def cancel_booking(request, booking_id):
    """
    Allows a user to cancel their booking only if the stored status matches "booked".
    """
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if request.method == "POST":
        if booking.status.lower() in ["booked", "Booked"]:  # Ensure status check works regardless of case
            booking.status = "Cancelled"
            booking.cancellation_time = now()  # Record cancellation timestamp
            booking.save()

            booking.slot.is_booked = False  # Free up the slot
            booking.slot.save()

            messages.success(request, "Your booking has been cancelled.")
            logger.info("User %s cancelled booking ID %s", request.user.username, booking_id)
        else:
            messages.error(request, "This booking cannot be cancelled.")
            logger.warning("User %s attempted to cancel booking ID %s with status %s",
                           request.user.username, booking_id, booking.status)

        return redirect("my_bookings")

    return render(request, "cancel_booking.html", {"booking": booking})

def add_slot(request):
    """
    Admin view to add a new slot.
    Only staff users can access this page.
    """
    if request.method == "POST":
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            # Ensure is_booked is set to False by default
            slot.is_booked = False
            slot.save()
            messages.success(request, "Slot added successfully!")
            logger.info("Slot id %s added by admin %s", slot.pk, request.user.username)
            # Redirect to a custom list page for slots if you have one,
            # or simply redirect back to the add slot page.
            return redirect("add_slot")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SlotForm()
    return render(request, "add_slot.html", {"form": form})


def admin_dashboard(request):
    """Displays the admin dashboard with booking and slot statistics."""
    total_bookings = Booking.objects.count()
    total_slots = Slot.objects.count()
    total_users = User.objects.count()
    total_locations = Location.objects.count()
    total_sports = Sport.objects.count()
    return render(
        request,
         "admin_dashboard.html",
        {
            "total_bookings": total_bookings,
            "total_slots": total_slots,
            "total_users": total_users,
            "total_locations": total_locations,
            "total_sports": total_sports,
        },
    )

def admin_list_bookings(request):
    """Displays a list of all bookings for admins."""
    bookings = Booking.objects.all()
    return render(request, "admin_list_bookings.html", {"bookings": bookings})

def admin_list_slots(request):
    """Displays a list of all slots for admins."""
    slots = Slot.objects.all()
    return render(request, "admin_list_slots.html", {"slots": slots})

def admin_add_slot(request):
    """Allows admins to add new slots."""
    if request.method == "POST":
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save()
            return redirect("admin_list_slots")
    else:
        form = SlotForm()
    return render(request, "admin_add_slot.html", {"form": form})

def admin_update_slot(request, slot_id):
    """Allows admins to update slot details."""
    slot = get_object_or_404(Slot, slot_id=slot_id)
    if request.method == "POST":
        form = SlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            return redirect("admin_list_slots")
    else:
        form = SlotForm(instance=slot)
    return render(request, "admin_update_slot.html", {"form": form})

def approve_booking(request, booking_id):
    """Allows admins to approve bookings."""
    booking = Booking.objects.get(pk=booking_id)
    booking.status = "Approved"
    booking.save()
    return redirect("admin_list_bookings")

def admin_cancel_booking(request, booking_id):
    """Allows admins to cancel bookings."""
    booking = Booking.objects.get(pk=booking_id)
    booking.status = "Cancelled"
    booking.save()
    return redirect("admin_list_bookings")

# def admin_add_booking(request):
#     """Allows admins to add new bookings by directly selecting an available slot."""
#     form = BookingAdminForm(request.POST or None)
#     if request.method == "POST":
#         if form.is_valid():
#             booking = form.save()
#             messages.success(request, f"Booking for slot ID {booking.slot.slot_id} created successfully.")
#             return redirect("admin_list_bookings")
#         else:
#             messages.error(request, "Please correct the errors in the form.")
#     return render(request, "admin_add_booking.html", {"form": form})


# def admin_update_booking(request, booking_id):
#     """Allows admins to update booking details."""
#     booking = Booking.objects.get(pk=booking_id)
#     if request.method == "POST":
#         form = BookingAdminUpdateForm(request.POST, instance=booking)
#         if form.is_valid():
#             form.save()
#             return redirect("admin_list_bookings")
#     else:
#         form = BookingAdminUpdateForm(instance=booking)
#     return render(request, "admin_update_booking.html", {"form": form, "booking_id": booking_id})


def admin_add_booking(request):
    """Allows admins to add new bookings by directly selecting an available slot."""
    now = timezone.now()
    available_slots = Slot.objects.filter(is_booked=False, date__gte=now.date()).order_by('date', 'time')
    form = BookingAdminForm(request.POST or None)
    form.fields['slot'].queryset = available_slots  # Set the filtered queryset
    if request.method == "POST":
        if form.is_valid():
            booking = form.save()
            messages.success(request, f"Booking for slot ID {booking.slot.slot_id} created successfully.")
            return redirect("admin_list_bookings")
        else:
            messages.error(request, "Please correct the errors in the form.")
    return render(request, "admin_add_booking.html", {"form": form})


def admin_update_booking(request, booking_id):
    """Allows admins to update booking details."""
    booking = get_object_or_404(Booking, pk=booking_id)
    now = timezone.now()
    available_slots = Slot.objects.filter(date__gte=now.date()).order_by('date', 'time')
    form = BookingAdminUpdateForm(request.POST or None, instance=booking)
    form.fields['slot'].queryset = available_slots  # Set the filtered queryset
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f"Booking ID {booking.booking_id} updated successfully.")
            return redirect("admin_list_bookings")
    else:
        form = BookingAdminUpdateForm(instance=booking)
        form.fields['slot'].queryset = available_slots  # Set the filtered queryset for the initial display
    return render(request, "admin_update_booking.html", {"form": form, "booking_id": booking_id})

def admin_delete_slot(request, slot_id):
    # Get the slot or 404 if it doesn't exist
    slot = get_object_or_404(Slot, slot_id=slot_id)

    if request.method == 'POST':
        # Allow deletion regardless of bookings
        slot.delete()
        messages.success(request, f"Slot {slot_id} deleted successfully, even if it was booked.")
        return redirect('admin_list_slots')  # Adjust this route name if needed

    return render(request, 'admin_delete_slot.html', {'slot_id': slot_id})


def admin_delete_booking(request, booking_id):
    """Allows admins to delete bookings."""
    try:
        booking = Booking.objects.get(pk=booking_id)
    except Booking.DoesNotExist:
        messages.error(request, f"No booking found with ID {booking_id}")
        return redirect("admin_list_bookings")

    if request.method == "POST":
        booking.delete()
        messages.success(request, f"Booking {booking_id} deleted successfully.")
        return redirect("admin_list_bookings")
    else:
        return render(request, "admin_delete_booking.html", {"booking_id": booking_id})

def admin_manage_bookings(request):
    """Renders the manage bookings page for admins."""
    return render(request, "manage_bookings.html")

def admin_manage_slots(request):
    """Renders the manage slots page for admins."""
    return render(request, "manage_slots.html")

def admin_slot_calendar(request):
    """View to display slots for a selected date."""
    selected_date = None
    slots = []

    if request.method == "POST":
        date_str = request.POST.get("date")
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                slots = Slot.objects.filter(date=selected_date)
            except ValueError:
                selected_date = None

    return render(
        request,
        "admin_slot_calendar.html",
        {"selected_date": selected_date, "slots": slots},
    )

def get_slot_data(request):
    """Returns slot data in JSON format for FullCalendar."""
    slots = Slot.objects.all()
    data = [
    {
        "title": f"{slot.location} - {slot.sport}",
        "start": slot.date.isoformat(),
        "url": f"/bookings/admin/slots/update/{slot.slot_id}/",  # Replace with your custom URL
    }
    for slot in slots
    ]
    return JsonResponse(data, safe=False)


