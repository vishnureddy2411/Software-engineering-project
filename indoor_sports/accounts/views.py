from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.hashers import make_password
import uuid  # For generating unique reset tokens

from .models import User, Profile

# Temporary storage for reset tokens (for production, store these in the database)
reset_tokens = {}

def login_view(request):
    """
    Handle user login via a POST request. If authentication is successful, 
    the user is logged in and redirected to the 'home' page; otherwise, 
    an error message is displayed.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


def user_profile(request, user_id):
    """
    Retrieve and display the user's profile based on the provided user_id.
    """
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'user_profile.html', {'user': user, 'profile': profile})


@login_required
def manage_profile(request):
    """
    Let the logged-in user manage/update their profile.
    """
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        profile.location = request.POST.get('location')
        # You can add additional fields update here if needed
        profile.save()
        return redirect('manage_profile')
    return render(request, 'manage_profile.html', {'profile': profile})


def home(request):
    """
    Render the home page.
    """
    return render(request, 'home.html')


# -------------------- Password Reset Functionality -------------------- #

def password_reset_request(request):
    """
    Handles password reset requests by sending an email with a reset link.
    """
    # Clear previous messages
    messages.get_messages(request).used = True  
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(emailid=email)
            token = str(uuid.uuid4())  # Generate a unique token
            reset_tokens[token] = user.userid  # Store the token with the user ID

            # Build the password reset link and send it via email
            reset_link = request.build_absolute_uri(reverse("password_reset_confirm", args=[token]))
            send_mail(
                "Password Reset Request",
                f"Click the link below to reset your password:\n\n{reset_link}",
                "noreply@indoresports.com",
                [email],
                fail_silently=False,
            )
            messages.success(request, "Password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "Email not found. Please enter a valid email.")

    return render(request, "password_reset.html")


def password_reset_confirm(request, token):
    """
    Handles password reset confirmation where the user sets a new password.
    """
    user_id = reset_tokens.get(token)
    if not user_id:
        messages.error(request, "Invalid or expired token.")
        return redirect("password_reset")

    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        if new_password == confirm_password:
            user = User.objects.get(userid=user_id)
            user.password = make_password(new_password)  # Securely hash the new password
            user.save()
            messages.success(request, "Password successfully reset! You can now log in.")
            del reset_tokens[token]  # Remove the token after use
            return redirect("loginpage")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "password_reset_confirm.html", {"token": token})


