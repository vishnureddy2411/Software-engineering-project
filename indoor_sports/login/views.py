from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from accounts.models import User, Admin
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    """
    Handles login for both regular users and admins.
    Redirects based on the user's role after successful authentication.
    """
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "").strip()

        logger.info(f"Login attempt for identifier: {identifier}")

        # User authentication
        user = User.objects.filter(username=identifier).first() or User.objects.filter(emailid=identifier).first()
        if user and (check_password(password, user.password) or password == user.password):
            if not user.is_active:
                messages.error(request, "User account is inactive. Contact support.")
                return redirect("loginpage")
            
            login(request, user)
            set_user_session(request, user)

            user.lastlogin = now()
            user.save(update_fields=["lastlogin"])
            logger.info(f"User {user.username} logged in successfully.")
            return redirect("user_dashboard")

        # Admin authentication
        admin = Admin.objects.filter(emailid=identifier).first()
        if admin and (check_password(password, admin.password) or password == admin.password):
            if not admin.is_verified or not admin.is_active:
                messages.error(request, "Admin access denied. Account not verified or inactive.")
                return redirect("loginpage")
            
            login(request, admin)
            set_admin_session(request, admin)

            admin.lastlogin = now()
            admin.save(update_fields=["lastlogin"])
            logger.info(f"Admin {admin.emailid} logged in successfully.")
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