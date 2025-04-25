from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from accounts.models import User, Admin
from bookings.models import Booking
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout
import logging

logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def login_view(request):
    """
    Handles login for both regular users and admins.
    Redirects based on the user's role after successful authentication.
    """
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "").strip()

        logger.info(f"Login attempt for identifier: {identifier}")
        print(f"Login attempt for identifier: {identifier}")

        # User authentication
        user = User.objects.filter(username=identifier).first() or User.objects.filter(emailid=identifier).first()
        if user and (check_password(password, user.password) or password == user.password):
            print(f"User found: {user.username} | Active: {user.is_active}")
            if not user.is_active:
                messages.error(request, "User account is inactive. Contact support.")
                return redirect("loginpage")
            
            login(request, user)
            set_user_session(request, user)

            user.lastlogin = now()
            user.save(update_fields=["lastlogin"])
            print(f"User {user.username} logged in successfully. Redirecting to user dashboard.")
            logger.info(f"User {user.username} logged in successfully.")

            # Extra logic: Redirect to review page for incomplete booking reviews
            booking = Booking.objects.filter(user=user, status__in=['booked', 'Booked']).order_by('-booking_date', '-time_slot').first()
            if booking is not None and not booking.submitted_review:
                print("Redirecting to review page for booking:", booking)
                logger.info(f"Redirecting {user.username} to review page for booking {booking.booking_id}.")
                return redirect('reviews_by_location_booking', 
                booking_id=booking.booking_id, location_id=booking.location.location_id, sport_id=booking.sport.sport_id)
            
            return redirect("user_dashboard")

        # Admin authentication
        admin = Admin.objects.filter(emailid=identifier).first()
        if admin and (check_password(password, admin.password) or password == admin.password):
            print(f"Admin found: {admin.emailid} | Verified: {admin.is_verified} | Active: {admin.is_active}")
            if not admin.is_verified or not admin.is_active:
                messages.error(request, "Admin access denied. Account not verified or inactive.")
                return redirect("loginpage")
            
            login(request, admin)
            set_admin_session(request, admin)

            admin.lastlogin = now()
            admin.save(update_fields=["lastlogin"])
            print(f"Admin {admin.emailid} logged in successfully. Redirecting to admin dashboard.")
            logger.info(f"Admin {admin.emailid} logged in successfully.")
            print("Session after login:", request.session.items())
            return redirect("admin_dashboard")

        # Invalid credentials
        print("Invalid username/email or password. Redirecting to login page.")
        messages.error(request, "Invalid username/email or password.")
        logger.warning(f"Login failed for identifier: {identifier}")
        return redirect("loginpage")

    return render(request, "login.html")

def logout_view(request):
    """
    Logs out the user/admin and clears all session data.
    """
    print("Logout view accessed.")  # Debugging message
    logout(request)  # Logs out the user/admin
    request.session.flush()  # Clears all session data
    messages.success(request, "You have been logged out successfully.")
    return redirect("loginpage")  # Redirects to the login page


def set_user_session(request, user):
    """
    Stores necessary user details in the session.
    """
    print(f"Setting session data for User: {user.username}")
    request.session["user_id"] = user.userid
    request.session["username"] = user.username
    request.session["email"] = user.emailid
    request.session["is_verified"] = bool(user.is_active)
    request.session["is_superuser"] = bool(user.is_superuser)
    request.session["is_staff"] = bool(user.is_staff)
    request.session["subscription"] = user.subscription
    request.session["referral_code"] = user.referral_code
    request.session["referred_by"] = user.referred_by_id if user.referred_by else None
    request.session["role"] = "user"
    request.session["is_authenticated"] = True
    request.session.modified = True
    request.session.save()
    print(f"User session set: {request.session.items()}")

def set_admin_session(request, admin):
    """
    Stores necessary admin details in the session.
    """
    print(f"Setting session data for Admin: {admin.emailid}")
    request.session["admin_id"] = admin.adminid
    request.session["admin_email"] = admin.emailid
    request.session["admin_name"] = f"{admin.firstname} {admin.lastname}"
    request.session["is_verified"] = bool(admin.is_verified)
    request.session["is_superuser"] = bool(admin.is_superuser)
    request.session["is_staff"] = bool(admin.is_staff)
    request.session["status"] = admin.status
    request.session["gender"] = admin.gender
    request.session["role"] = "admin"
    request.session["is_authenticated"] = True
    request.session.modified = True
    request.session.save()
    print(f"Admin session set: {request.session.items()}")


    
    