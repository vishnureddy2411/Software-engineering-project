from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from accounts.models import User, Admin
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login  # Use Django's built-in login
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    """
    Handles login for both regular users and admins.
    Redirects based on the user's role after successful authentication.
    Displays error messages for invalid credentials.
    Stores a role in session so that the role check can be done globally.
    """
    if request.method == "POST":
        # Extract identifier (username/email) and password from POST request
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "").strip()

        logger.info("Login attempt for identifier: %s", identifier)

        user = None
        admin = None

        # Check if the identifier matches a regular User (first by username, then by emailid)
        try:
            user = User.objects.get(username=identifier)
            logger.info("User found by username: %s", identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(emailid=identifier)
                logger.info("User found by emailid: %s", identifier)
            except User.DoesNotExist:
                user = None
                logger.info("No user found with identifier: %s", identifier)

        # Authenticate the User
        if user and check_password(password, user.password):
            login(request, user)
            # Set session variable for role
            request.session["role"] = "user"
            user.lastlogin = now()
            user.save(update_fields=["lastlogin"])
            logger.info("User %s logged in successfully. Session data: %s", 
                        user.username, request.session.items())
            messages.success(request, "Login successful! Redirecting to User Dashboard.")
            return redirect("user_dashboard")
        elif user:
            logger.warning("Invalid password for user: %s", identifier)
            messages.error(request, "Invalid password. Please try again.")
            return redirect("loginpage")

        # If not a regular user, try to authenticate as an Admin using emailid only
        try:
            admin = Admin.objects.get(emailid=identifier)
            logger.info("Admin found with emailid: %s", identifier)
        except Admin.DoesNotExist:
            admin = None
            logger.info("No admin found with emailid: %s", identifier)

        if admin and check_password(password, admin.password):
            login(request, admin)
            # Set session variable for role
            request.session["role"] = "admin"
            admin.lastlogin = now()
            admin.save(update_fields=["lastlogin"])
            logger.info("Admin %s logged in successfully. Session data: %s", 
                        admin, request.session.items())
            messages.success(request, "Login successful! Redirecting to Admin Dashboard.")
            return redirect("admin_dashboard")
        elif admin:
            logger.warning("Invalid password for admin: %s", identifier)
            messages.error(request, "Invalid password. Please try again.")
            return redirect("loginpage")

        logger.error("Login failed: Invalid credentials for identifier %s", identifier)
        messages.error(request, "Invalid username/email or password. Please try again.")
        return redirect("loginpage")

    # Render the login page for GET requests
    return render(request, "login.html")


def logout_view(request):
    """
    Logs out the user/admin and clears all session data.
    """
    logger.info("Logging out user with session data: %s", request.session.items())
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("loginpage")


def set_session(request, user_id, role):
    """
    Helper function to set session data.
    """
    request.session["user_id"] = user_id
    request.session["role"] = role
    request.session["is_authenticated"] = True
    logger.info("Session set: %s", request.session.items())
