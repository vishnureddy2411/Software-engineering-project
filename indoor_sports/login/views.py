# from django.shortcuts import render, redirect
# from django.contrib.auth import login, logout
# from django.contrib.auth.hashers import check_password
# from django.contrib import messages
# from django.utils.timezone import now
# from django.views.decorators.csrf import csrf_protect
# from django.http import HttpResponse
# from accounts.models import User, Admin
# from bookings.models import Booking
# import logging

# logger = logging.getLogger(__name__)

# @csrf_protect
# def login_view(request):
#     """
#     Handles login for both regular users and admins.
#     Redirects based on the user's role after successful authentication.
#     """
#     if request.method == "POST":
#         identifier = request.POST.get("identifier", "").strip()
#         password = request.POST.get("password", "").strip()

#         logger.info(f"Login attempt for identifier: {identifier}")
#         print(f"Login attempt for identifier: {identifier}")

#         # User authentication
#         user = User.objects.filter(username=identifier).first() or User.objects.filter(emailid=identifier).first()
#         if user and (check_password(password, user.password) or password == user.password):
#             print(f"User found: {user.username} | Active: {user.is_active}")
#             if not user.is_active:
#                 messages.error(request, "User account is inactive. Contact support.")
#                 return redirect("loginpage")

#             login(request, user)
#             set_user_session(request, user)

#             user.lastlogin = now()
#             user.save(update_fields=["lastlogin"])

#             print(f"User {user.username} logged in successfully. Redirecting to user dashboard.")
#             logger.info(f"User {user.username} logged in successfully.")

#             # Debugging session before redirect
#             print("User session before redirect:", request.session.items())

#             # Redirect Logic: Check for incomplete booking reviews
#             incomplete_reviews = Booking.objects.filter(
#                 user=user,
#                 status__in=['booked', 'Booked'],
#                 submitted_review=False
#             ).order_by('-booking_date', '-time_slot').first()

#             if incomplete_reviews:
#                 print("Redirecting to review page for booking:", incomplete_reviews)
#                 logger.info(
#                     f"Redirecting {user.username} to review page for booking {incomplete_reviews.booking_id}."
#                 )
#                 return redirect(
#                     'reviews_by_location_booking',
#                     booking_id=incomplete_reviews.booking_id,
#                     location_id=incomplete_reviews.location.location_id,
#                     sport_id=incomplete_reviews.sport.sport_id
#                 )

#             return redirect("user_dashboard")

#         # Admin authentication
#         admin = Admin.objects.filter(emailid=identifier).first()
#         if admin and (check_password(password, admin.password) or password == admin.password):
#             print(f"Admin found: {admin.emailid} | Verified: {admin.is_verified} | Active: {admin.is_active}")
#             if not admin.is_verified or not admin.is_active:
#                 messages.error(request, "Admin access denied. Account not verified or inactive.")
#                 return redirect("loginpage")

#             login(request, admin)
#             set_admin_session(request, admin)

#             admin.lastlogin = now()
#             admin.save(update_fields=["lastlogin"])

#             print(f"Admin {admin.emailid} logged in successfully. Redirecting to admin dashboard.")
#             logger.info(f"Admin {admin.emailid} logged in successfully.")

#             # Debugging session before redirect
#             print("Admin session before redirect:", request.session.items())

#             # return HttpResponse(f"Session after login: {dict(request.session.items())}")  # Debug step
#             print(f"Debug: Session Data Before Redirect to Dashboard -> {dict(request.session.items())}")

#             return redirect("admin_dashboard")

#         # Invalid credentials
#         print("Invalid username/email or password. Redirecting to login page.")
#         messages.error(request, "Invalid username/email or password.")
#         logger.warning(f"Login failed for identifier: {identifier}")
#         return redirect("loginpage")
    

#     return render(request, "login.html")

# def logout_view(request):
#     """
#     Logs out the user/admin and clears all session data.
#     """
#     print("Logout view accessed.")
#     logout(request)
#     request.session.flush()
#     messages.success(request, "You have been logged out successfully.")
#     return redirect("loginpage")

# def set_user_session(request, user):
#     """
#     Stores necessary user details in the session.
#     """
#     print(f"Setting session data for User: {user.username}")
#     request.session["user_id"] = user.userid
#     request.session["username"] = user.username
#     request.session["email"] = user.emailid
#     request.session["is_verified"] = bool(user.is_active)
#     request.session["is_superuser"] = bool(user.is_superuser)
#     request.session["is_staff"] = bool(user.is_staff)
#     request.session["subscription"] = user.subscription
#     request.session["referral_code"] = user.referral_code
#     request.session["referred_by"] = user.referred_by_id if user.referred_by else None
#     request.session["role"] = "user"
#     request.session["is_authenticated"] = True
#     request.session.modified = True
#     request.session.save()
#     print(f"User session set: {request.session.items()}")

# def set_admin_session(request, admin):
#     """
#     Stores necessary admin details in the session.
#     """
#     print(f"Setting session data for Admin: {admin.emailid}")
#     request.session["admin_id"] = admin.adminid
#     request.session["admin_email"] = admin.emailid
#     request.session["admin_name"] = f"{admin.firstname} {admin.lastname}"
#     request.session["is_verified"] = bool(admin.is_verified)
#     request.session["is_superuser"] = bool(admin.is_superuser)
#     request.session["is_staff"] = bool(admin.is_staff)
#     request.session["status"] = admin.status
#     request.session["gender"] = admin.gender
#     request.session["role"] = "admin"
#     request.session["is_authenticated"] = True
#     request.session.modified = True
#     request.session.save()
#     print(f"Admin session set: {request.session.items()}")

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from accounts.models import User, Admin
from bookings.models import Booking
import logging

logger = logging.getLogger(__name__)

@csrf_protect
def login_view(request):
    """
    Handles login for both regular users and admins using a custom auth backend.
    Redirects based on the user's role after successful authentication.
    """
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "").strip()

        logger.info(f"Login attempt for identifier: {identifier}")
        
        # Use the custom backend to authenticate
        user_or_admin = authenticate(request, username=identifier, password=password)

        if user_or_admin:
            login(request, user_or_admin)

            if isinstance(user_or_admin, User):
                if not user_or_admin.is_active:
                    messages.error(request, "User account is inactive. Contact support.")
                    return redirect("loginpage")

                set_user_session(request, user_or_admin)
                user_or_admin.lastlogin = now()
                user_or_admin.save(update_fields=["lastlogin"])

                logger.info(f"User {user_or_admin.username} logged in successfully.")
                
                # Check for incomplete reviews
                incomplete_reviews = Booking.objects.filter(
                    user=user_or_admin,
                    status__in=['booked', 'Booked'],
                    submitted_review=False
                ).order_by('-booking_date', '-time_slot').first()

                if incomplete_reviews:
                    return redirect(
                        'reviews_by_location_booking',
                        booking_id=incomplete_reviews.booking_id,
                        location_id=incomplete_reviews.location.location_id,
                        sport_id=incomplete_reviews.sport.sport_id
                    )

                return redirect("user_dashboard")

            elif isinstance(user_or_admin, Admin):
                if not user_or_admin.is_verified or not user_or_admin.is_active:
                    messages.error(request, "Admin access denied. Account not verified or inactive.")
                    return redirect("loginpage")

                set_admin_session(request, user_or_admin)
                user_or_admin.lastlogin = now()
                user_or_admin.save(update_fields=["lastlogin"])

                logger.info(f"Admin {user_or_admin.emailid} logged in successfully.")
                return redirect("admin_dashboard")

        # Invalid credentials
        messages.error(request, "Invalid username/email or password.")
        logger.warning(f"Login failed for identifier: {identifier}")
        return redirect("loginpage")

    return render(request, "login.html")



def logout_view(request):
    """
    Logs out the user/admin and clears all session data.
    """
    logout(request)
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("loginpage")


def set_user_session(request, user):
    """
    Stores necessary user details in the session.
    """
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


def set_admin_session(request, admin):
    """
    Stores necessary admin details in the session.
    """
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
