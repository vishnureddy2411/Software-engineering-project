from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User, Admin
from django.contrib.auth.decorators import login_required
import logging
from sports.models import Event, Location, Sport
from django.db.models import Q
from .forms import EventForm

logger = logging.getLogger(__name__)

@login_required
def user_dashboard(request):
    """
    Displays the user dashboard. Ensures the user is authenticated and assigned the role of 'user'.
    """
    # Clear existing messages
    list(messages.get_messages(request))

    # Authentication and Role Check
    if not request.session.get("is_authenticated") or request.session.get("role") != "user":
        messages.error(request, "Access denied. Please log in.")
        return redirect("loginpage")

    user_id = request.session.get("user_id")
    if not user_id:
        logger.error("Session user_id is missing.")
        messages.error(request, "Session expired. Please log in again.")
        return redirect("loginpage")

    try:
        user = User.objects.get(userid=user_id)
        logger.info(f"Accessing user dashboard: User ID {user.userid}")
    except User.DoesNotExist:
        logger.error(f"User not found: User ID {user_id}")
        messages.error(request, "User not found. Please log in again.")
        return redirect("loginpage")

    # Fetch locations
    locations = Location.objects.all()

    # Get selected location from GET request
    selected_location_id = request.GET.get('location_id', 'all')  # Default is 'all' if no location is selected

    # Fetch sports based on selected location
    if selected_location_id != 'all':
        sports = Sport.objects.filter(location_id=selected_location_id)
    else:
        sports = Sport.objects.all()

    return render(request, 'user_dashboard.html', {
        'locations': locations,
        'sports': sports,
        'selected_location_id': selected_location_id
    })


def admin_dashboard(request):
    """
    Displays the admin dashboard.
    Ensures the admin is authenticated and has the correct role.
    """
    list(messages.get_messages(request))  # Clear messages

    if not is_role_valid(request, "admin"):
        messages.warning(request, "You do not have permission to access this page.")
        return redirect("loginpage")

    try:
        admin_id = request.session.get("admin_id")
        admin = Admin.objects.get(adminid=admin_id)
        logger.info(f"Accessing admin dashboard: Admin ID {admin.adminid}")
    except Admin.DoesNotExist:
        logger.error(f"Admin not found: Admin ID {admin_id}")
        messages.error(request, "Admin not found. Please log in again.")
        return redirect("loginpage")

    return render(request, "admin_dashboard.html", {"last_login": admin.lastlogin})


def is_role_valid(request, expected_role):
    role = request.session.get("role")
    admin_id = request.session.get("admin_id")
    user_id = request.session.get("user_id")  # Add user_id for user validation

    print(f"Debug: Session Data -> {dict(request.session.items())}")  # Debug print

    if role != expected_role:
        print(f"Debug: Role mismatch! Expected: {expected_role}, Found: {role}")
        return False

    # ✅ Admin Validation
    if role == "admin" and admin_id:
        try:
            admin = Admin.objects.get(adminid=admin_id)
            print(f"Debug: Admin found -> {admin.emailid} | Verified: {admin.is_verified} | Active: {admin.is_active}")
            
            if not admin.is_verified or not admin.is_active:
                print("Debug: Admin is not verified or not active!")
                return False

            return True  # Admin is valid

        except Admin.DoesNotExist:
            print(f"Debug: Admin not found in DB! Admin ID: {admin_id}")
            return False

    # ✅ User Validation (Newly Added)
    if role == "user" and user_id:
        try:
            user = User.objects.get(userid=user_id)
            print(f"Debug: User found -> {user.username}  | Active: {user.is_active}")
            
            if not user.is_active:
                print("Debug: User is not active!")
                return False

            return True  # User is valid

        except User.DoesNotExist:
            print(f"Debug: User not found in DB! User ID: {user_id}")
            return False

    return False  # Default return False if no match




def admin_card_01(request):
    return render(request, 'admin_card_01.html')

@login_required
# Home Page
def home(request):
    upcoming_events = Event.objects.filter(status="Upcoming").order_by('event_date')
    past_events = Event.objects.filter(status="Completed").order_by('-event_date')

    return render(request, 'home.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    })




@login_required
def edit_profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)  # get profile if it exists

    if request.method == 'POST':
        # Update User fields only if the value is provided
        user.firstname = request.POST.get('firstname', user.firstname)
        user.lastname = request.POST.get('lastname', user.lastname)
        user.username = request.POST.get('username', user.username)
        user.emailid = request.POST.get('emailid', user.emailid)
        user.contactnumber = request.POST.get('contactnumber', user.contactnumber)
        user.address = request.POST.get('address', user.address)
        user.city = request.POST.get('city', user.city)
        user.state = request.POST.get('state', user.state)
        user.country = request.POST.get('country', user.country)
        user.zip_code = request.POST.get('zip_code', user.zip_code)
        user.gender = request.POST.get('gender', user.gender)

        user.save()

        # If user has a profile, update profile fields
        if profile:
            profile.bio = request.POST.get('bio', profile.bio)
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('edit_profile')  # or wherever you want to redirect

    context = {
        'user': user
    }
    return render(request, 'edit_profile.html', context)


def edit_profile_admin(request):
    # Get the logged-in user (assuming the user is an instance of the Admin model)
    admin = request.user

    # Handle the POST request to update the profile
    if request.method == 'POST':
        # Update the admin's details with the data from the form
        admin.firstname = request.POST.get('firstname', admin.firstname)
        admin.lastname = request.POST.get('lastname', admin.lastname)
        admin.emailid = request.POST.get('emailid', admin.emailid)
        admin.contactnumber = request.POST.get('contactnumber', admin.contactnumber)
        admin.address = request.POST.get('address', admin.address)
        admin.city = request.POST.get('city', admin.city)
        admin.state = request.POST.get('state', admin.state)
        admin.country = request.POST.get('country', admin.country)
        admin.zip_code = request.POST.get('zip_code', admin.zip_code)
        admin.gender = request.POST.get('gender', admin.gender)

        # Save the updated admin profile
        admin.save()

        # Display a success message and redirect back to the profile page
        messages.success(request, 'Admin profile updated successfully.')
        return redirect('edit_profile_admin')  # Redirect back to this view after saving

    # Pass the admin instance to the template for pre-populating the form
    context = {
        'admin': admin
    }
    
    # Render the form with the admin's current details
    return render(request, 'edit_profile_admin.html', context)
# View Bookings
def view_bookings(request):
    return render(request, 'view_bookings.html')

# View Payments
def view_payments(request):
    return render(request, 'view_payments.html')
# Add Users
def add_users(request):
    return render(request, 'add_users.html')

def add_admins(request):
    return render(request, 'add_admins.html')


# Contact Page
def contact(request):
    return render(request, 'contact.html')


def view_users(request):

    #  Handle Delete User (POST request)

    if request.method == 'POST':

        user_id_to_delete = request.POST.get('delete_user_id')

        if user_id_to_delete:

            user_to_delete = get_object_or_404(User, userid=user_id_to_delete)

            user_to_delete.delete()

            messages.success(request, "User deleted successfully.")

            return redirect('view_users')  # Redirect to refresh the list
 
    #  Handle Search Query (GET request)

    query = request.GET.get('q')

    if query:

        users = User.objects.filter(

            Q(username__icontains=query) |

            Q(firstname__icontains=query) |

            Q(lastname__icontains=query) |

            Q(emailid__icontains=query)

        )

    else:

        users = User.objects.all()
 
    return render(request, 'view_users.html', {'users': users, 'query': query})
 

def admin_card_03(request):
    return render(request, 'admin_card_03.html')

def add_slot(request):
    # Your logic to add a slot
    return render(request, 'add_slot.html')

def list_events(request):
    events = Event.objects.all()
    return render(request, 'list_events.html', {'events': events})

def create_event(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Event created successfully!")
        return redirect('list_events')
    return render(request, 'create_event.html', {'form': form})

def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, "Event updated successfully!")
        return redirect('list_events')
    return render(request, 'update_event.html', {'form': form})

def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted.")
        return redirect('list_events')
    return render(request, 'delete_event.html', {'event': event})

#sports
def view_sports(request):
    """
    Displays all sports with full details.
    """
    sports = Sport.objects.all()  # Retrieve all sports
    return render(request, 'view_sports.html', {'sports': sports})
 
def add_sport(request):
    """
    Handles adding a new sport with complete information.
    """
    locations = Location.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        location_id = request.POST.get('location_id')
        description = request.POST.get('description', '')
        image_path = request.POST.get('image_path', '')
        price = request.POST.get('price')
        peak_price = request.POST.get('peak_price')
        peak_hours_start = request.POST.get('peak_hours_start')
        peak_hours_end = request.POST.get('peak_hours_end')
        available = request.POST.get('available')
 
        location = Location.objects.get(location_id=location_id)  # Fetch location instance
 
        # Create the sport with all fields
        Sport.objects.create(
            name=name,
            category=category,
            location=location,
            description=description,
            image_path=image_path,
            price=price,
            peak_price=peak_price,
            peak_hours_start=peak_hours_start,
            peak_hours_end=peak_hours_end,
            available=available,
        )
        return redirect('view_sports')
 
    return render(request, 'add_sport.html', {'locations': locations})
 
 
 
 
 
def del_sport(request, sport_id):
    """
    Handles fetching sport details and confirmation before deletion.
    """
    # Fetch the sport instance using sport_id
    sport = get_object_or_404(Sport, sport_id=sport_id)
    locations = Location.objects.all()  # Fetch all locations for the dropdown, if needed
 
    if request.method == 'POST':  # Confirm deletion
        sport.delete()  # Delete the sport
        return redirect('view_sports')  # Redirect after deletion
 
    # Render the confirmation page with sport details auto-populated
    return render(request, 'del_sport.html', {'sport': sport, 'locations': locations})
 
 
 
def update_sport(request, sport_id):
    """Fetch and populate sport details in the update form for editing."""
    sport = get_object_or_404(Sport, sport_id=sport_id)
    locations = Location.objects.all()  # Fetch all locations for dropdown
 
    if request.method == 'POST':
        sport.name = request.POST.get('name', sport.name)
        sport.category = request.POST.get('category', sport.category)
        sport.description = request.POST.get('description', sport.description)
        sport.image_path = request.POST.get('image_path', sport.image_path)
        sport.price = request.POST.get('price', sport.price)
        sport.peak_price = request.POST.get('peak_price', sport.peak_price)
        sport.peak_hours_start = request.POST.get('peak_hours_start', sport.peak_hours_start)
        sport.peak_hours_end = request.POST.get('peak_hours_end', sport.peak_hours_end)
        sport.available = request.POST.get('available', sport.available)
        sport.location_id = request.POST.get('location_id', sport.location_id)
 
        sport.save()
        return redirect('view_sports')  # Redirect to sports list after update
 
    return render(request, 'update_sport.html', {'sport': sport, 'locations': locations})


def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def Terms_service(request):
    return render(request, 'Terms_service.html')

def about_us(request):
    return render(request, 'about_us.html')
