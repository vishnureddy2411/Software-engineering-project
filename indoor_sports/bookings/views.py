import calendar
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from sports.models import Location, Sport
from bookings.models import Slot, Booking
from bookings.forms import SlotForm
from .utils import AvailabilityHTMLCalendar
from accounts.models import User, Admin

import logging
logger = logging.getLogger(__name__)



def choose_location(request):
    locations = Location.objects.all().order_by('name')
    if request.method == "POST":
        location_id = request.POST.get("location")
        if location_id:
            logger.info("Location %s selected by user %s", location_id, request.user.username)
            return redirect("choose_sport", location_id=location_id)
        messages.error(request, "Please select a location.")
    return render(request, "choose_location.html", {"locations": locations})

def choose_sport(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    sports = Sport.objects.filter(location=location)
    if request.method == "POST":
        sport_id = request.POST.get("sport")
        if sport_id:
            logger.info("Sport %s chosen at location %s by user %s", sport_id, location.name, request.user.username)
            return redirect("choose_date", location_id=location_id, sport_id=sport_id)
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
    location = get_object_or_404(Location, pk=location_id)
    sport = get_object_or_404(Sport, pk=sport_id)

    try:
        year = int(request.GET.get("year", date.today().year))
        month = int(request.GET.get("month", date.today().month))
        if month < 1:
            year -= 1
            month = 12
        elif month > 12:
            year += 1
            month = 1
    except (ValueError, TypeError):
        year, month = date.today().year, date.today().month

    availability = {}
    _, num_days = calendar.monthrange(year, month)
    
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        day_str = current_date.strftime("%Y-%m-%d")
        slots_available = Slot.objects.filter(
            date=current_date,
            location=location,
            sport=sport,
            is_booked=False
        ).exists()
        availability[day_str] = slots_available

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
    Handles POST requests to redirect to the confirm_booking view.
    """
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        logger.error("Invalid date format: %s", date)
        messages.error(request, "Invalid date format. Please try again.")
        return redirect("choose_date", location_id=location_id, sport_id=sport_id)
    location = get_object_or_404(Location, pk=location_id)
    sport = get_object_or_404(Sport, pk=sport_id)
    
    slots = Slot.objects.filter(
        date=selected_date,
        location=location,
        sport=sport,
        is_booked=False
    )
    
    logger.info("Slots for %s at %s (%s): %d slots", selected_date, location.name, sport.name, slots.count())
    if not slots.exists():
        messages.info(request, f"No slots available on {selected_date}. Please choose another date.")
        return redirect("choose_date", location_id=location_id, sport_id=sport_id)
    
    # Handle the POST request where the user selects a slot and clicks Next.
    if request.method == "POST":
        slot_id = request.POST.get("slot")
        if slot_id:
            return redirect("confirm_booking", slot_id=slot_id)
        else:
            messages.error(request, "Please select a slot.")
            # Fall through to re-rendering the page with an error message
    context = {
        "slots": slots,
        "date": selected_date,
        "location": location,
        "sport": sport,
        "location_id": location.pk,  # Use pk in case id is not defined
        "sport_id": sport.pk,
    }
    return render(request, "list_slots.html", context)

def confirm_booking(request, slot_id):
    slot = get_object_or_404(Slot, pk=slot_id)
    if slot.is_booked:
        messages.error(request, "This slot is no longer available. Please select another slot.")
        return redirect("choose_date", location_id=slot.location.pk, sport_id=slot.sport.pk)
    
    if request.method == "POST":
        # Create the booking without any equipment or quantity details.
        booking = Booking.objects.create(
            user=request.user,
            
            sport=slot.sport,
            slot=slot,
            location=slot.location,
            status="Booked",
            time_slot=slot.time
        )
        slot.is_booked = True
        slot.save()
        logger.info("User %s confirmed booking %s for slot %s", request.user.username, booking.id, slot)
        messages.success(request, "Your booking has been confirmed!")
        # Redirect to booking success page where equipment selection can be offered.
        return redirect("booking_success")
    
    # Render confirmation details for the slot.
    return render(request, "confirm_booking.html", {"slot": slot})



def booking_success(request):
    logger.info("Booking success page accessed by user %s", request.user.username)
    return render(request, "booking_success.html")

def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    logger.info("User %s accessed their bookings. Total: %d", request.user.username, bookings.count())
    return render(request, "my_bookings.html", {"bookings": bookings})


def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    logger.info("User %s is viewing details of booking ID %s", request.user.username, booking_id)
    return render(request, "booking_detail.html", {"booking": booking})

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    if request.method == "POST":
        if booking.status in ["Booked", "Pending"]:
            booking.status = "Cancelled"
            booking.save()
            booking.slot.is_booked = False
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

