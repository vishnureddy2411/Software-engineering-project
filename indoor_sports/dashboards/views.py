from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User, Admin
from django.contrib.auth.decorators import login_required
import logging
from sports.models import Event, Location, Sport
from django.db.models import Q


logger = logging.getLogger(__name__)


def user_dashboard(request):
    """
    Displays the user dashboard. Ensures the user is authenticated and is assigned the role of 'user'.
    """
    # Clear existing messages
    list(messages.get_messages(request))

    # Check if user has the correct role (e.g., 'user')
    if not is_role_valid(request, "user"):
        messages.warning(request, "You do not have permission to access this page.")
        return redirect("loginpage")

    try:
        user = User.objects.get(userid=request.session["user_id"])
        logger.info(f"Accessing user dashboard: User ID {user.userid}")
    except User.DoesNotExist:
        logger.error(f"User not found: User ID {request.session.get('user_id')}")
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


# Home Page
def home(request):
    upcoming_events = Event.objects.filter(status="Upcoming").order_by('event_date')
    past_events = Event.objects.filter(status="Completed").order_by('-event_date')

    return render(request, 'home.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events
    })

# views.py
def view_sports(request):
    sports = Sport.objects.all()  # or you can filter if needed
    return render(request, 'view_sports.html', {'sports': sports})


# Add Sport
def add_sport(request):
    locations = Location.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        location_id = request.POST.get('location_id')
        description = request.POST.get('description', '')
        image_path = request.POST.get('image_path', '')

        location = Location.objects.get(id=location_id)
        Sport.objects.create(
            sport_name=name,
            category=category,
            location=location,
            description=description,
            image_path=image_path
        )
        return redirect('view_sports')

    return render(request, 'add_sport.html', {'locations': locations})

# Delete Sport
def del_sport(request):
    locations = Location.objects.all()
    message = ''
    if request.method == 'POST':
        name = request.POST['name']
        location_id = request.POST['location_id']
        deleted, _ = Sport.objects.filter(sport_name=name, location_id=location_id).delete()
        message = f"{deleted} sport(s) deleted."
      

    return render(request, 'del_sport.html', {'locations': locations, 'message': message})
@ login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.emailid = request.POST.get('emailid', '')
        user.save()
        return redirect('user_dashboard')

    return render(request, 'edit_profile.html', {'user': user})


# Update Sport
def update_sport(request):
    return render(request, 'update_sport.html')

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
