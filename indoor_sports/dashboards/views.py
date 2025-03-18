from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User, Admin
from django.contrib.auth.decorators import login_required
import logging
from sports.models import Event, Location, Sport
from django.db.models import Q


logger = logging.getLogger(__name__)

# # User Dashboard
# def user_dashboard(request):
#     """
#     Displays the user dashboard. Ensures the user is authenticated and is assigned the role of 'user'.
#     """
#     list(messages.get_messages(request))  # Clear existing messages

#     if not is_role_valid(request, "user"):
#         messages.warning(request, "You do not have permission to access this page.")
#         return redirect("loginpage")

#     try:
#         user = User.objects.get(userid=request.session["user_id"])
#         logger.info(f"Accessing user dashboard: User ID {user.userid}")
#     except User.DoesNotExist:
#         logger.error(f"User not found: User ID {request.session.get('user_id')}")
#         messages.error(request, "User not found. Please log in again.")
#         return redirect("loginpage")

#     # # Fetch locations and sports based on selected location
#     # locations = Location.objects.all()
#     # selected_location_id = request.GET.get('id')

#     # if selected_location_id and selected_location_id != 'all':
#     #     sports = Sport.objects.filter(location_id=selected_location_id)
#     # else:
#     #     sports = Sport.objects.all()

#     # # Render user dashboard
#     # return render(request, "user_dashboard.html", {
#     #     "last_login": user.lastlogin,
#     #     "locations": locations,
#     #     "sports": sports,
#     #     "selected_location_id": selected_location_id
#     # })

#     locations = Location.objects.all()
#     selected_location_id = request.GET.get('id')
 
#     if selected_location_id and selected_location_id != 'all':
#         sports = Sport.objects.filter(id=selected_location_id)
#     else:
#         sports = Sport.objects.all()
 
#     return render(request, 'user_dashboard.html', {
#         'locations': locations,
#         'sports': sports,
#         'selected_location_id': selected_location_id
   
#     })


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

# Admin Dashboard
def admin_dashboard(request):
    """
    Displays the admin dashboard. Ensures the admin is authenticated and has the role of 'admin'.
    """
    list(messages.get_messages(request))  # Clear existing messages

    if not is_role_valid(request, "admin"):
        messages.warning(request, "You do not have permission to access this page.")
        return redirect("loginpage")

    try:
        admin = Admin.objects.get(adminid=request.session["user_id"])
        logger.info(f"Accessing admin dashboard: Admin ID {admin.adminid}")
    except Admin.DoesNotExist:
        logger.error(f"Admin not found: Admin ID {request.session.get('user_id')}")
        messages.error(request, "Admin not found. Please log in again.")
        return redirect("loginpage")

    return render(request, "admin_dashboard.html", {"last_login": admin.lastlogin})

# Helper function to validate user role
def is_role_valid(request, expected_role):
    role = request.session.get("role")
    if role != expected_role:
        logger.warning(f"Invalid role access attempt. Expected: {expected_role}, Found: {role}")
        return False
    return True

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