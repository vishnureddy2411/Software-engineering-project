from venv import logger
from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from accounts.models import Admin, User
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlencode
import smtplib
import traceback
import os
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

import requests
from django.http import JsonResponse

def get_location_from_zipcode(request):
    """Fetch location data using PositionStack API."""
    zipcode = request.GET.get('zipcode')
    if not zipcode:
        return JsonResponse({'error': 'No ZIP code provided.'}, status=400)

    # PositionStack API details
    api_key = '5171b95fc73f57b6720ab769fbe67f06'  # Replace with your actual API key
    url = f"https://api.positionstack.com/v1/forward?access_key={api_key}&query={zipcode}, United States"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get('data') and len(data['data']) > 0:
            return JsonResponse(data['data'][0])  # Return the first match
        else:
            return JsonResponse({'error': 'No data found for this ZIP code.'}, status=404)
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")  # Debugging
        return JsonResponse({'error': 'Unable to fetch location data.'}, status=500)

        
# from referrals.utils import process_referral  # Optional: hook for referral processing


def generate_referral_code(user_id):
    """Generate a unique referral code based on user_id."""
    return f"USER{user_id}"


@csrf_exempt
def check_email_exists(request):
    """Check if an email already exists in the database."""
    if request.method == "POST":
        emailid = request.POST.get("emailid", "").strip()
        print(f"Received email: {emailid}")  # Debugging

        if User.objects.filter(emailid__iexact=emailid).exists():
            print("Email exists!")
            return JsonResponse({"exists": True}, status=200)
        print("Email does not exist!")
        return JsonResponse({"exists": False}, status=200)

    print("Invalid request!")
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def check_username(request):
    """AJAX view to check if a username is already taken."""
    if request.method == 'POST':
        username = request.POST.get('username')
        print(f"Checking username: {username}")  # Debug output
        if username:
            username_exists = User.objects.filter(username=username).exists()
            return JsonResponse({'exists': username_exists})
        else:
            return JsonResponse({'exists': False})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def register_user(request):
    """
    Handle self-registration for a new user.
    Processes form data, validates inputs, applies referral logic,
    sends a welcome email, and auto-logs in the user.
    """
    if request.method == "POST":
        print("Received POST data:", request.POST)
        username = request.POST.get("username", "").strip()
        firstname = request.POST.get("firstname", "").strip()
        lastname = request.POST.get("lastname", "").strip()
        emailid = request.POST.get("emailid", "").strip()
        password = request.POST.get("password", "").strip()
        contactnumber = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        zip_code = request.POST.get("zip_code", "").strip()
        gender = request.POST.get("gender", "").strip()
        referral_code_used = request.POST.get("referral_code", "").strip()

        if not emailid or not password:
            messages.error(request, "Email and password are required.")
            return redirect("register_user")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another one.")
            return redirect("register_user")

        if User.objects.filter(emailid=emailid).exists():
            messages.error(request, "Email already registered. Please use another email.")
            return redirect("register_user")

        referred_by = None
        referral_points = 0
        if referral_code_used:
            referred_by_user = User.objects.filter(referral_code=referral_code_used).first()
            if referred_by_user:
                referred_by = referred_by_user
                referral_points = 10
            else:
                messages.warning(request, "Invalid referral code. Registration will continue without referral.")

        user = User.objects.create(
            firstname=firstname,
            lastname=lastname,
            emailid=emailid,
            username=username,
            password=make_password(password),
            contactnumber=contactnumber,
            address=address,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
            gender=gender,
            subscription="unsubscribed",
            referral_points=referral_points,
            referred_by=referred_by
        )

        # Generate and update referral code after user is saved
        user.referral_code = generate_referral_code(user.userid)
        user.save()

        if referred_by:
            referred_by.referral_points += 10
            referred_by.save()

        send_mail(
            'Welcome to Indore Sports!',
            f'Hi {lastname}, thank you for registering with us.',
            'saivishnutallapureddy@gmail.com',
            [emailid],
            fail_silently=False,
        )

        request.session["user_id"] = user.userid
        request.session["role"] = "user"

        messages.success(request, "Registration successful! Redirecting to your Login Page.")
        return redirect("loginpage")

    return render(request, "register_user.html")


def is_role_valid(request, expected_role):
    """
    Validates if the logged-in user has the expected role.
    Ensures admin exists and is verified for admin-related actions.
    """
    role = request.session.get("role")
    admin_id = request.session.get("admin_id")

    print(f"Checking role validity: Expected: {expected_role}, Found: {role}, Admin ID: {admin_id}")
    logger.info(f"Checking role validity: Expected: {expected_role}, Found: {role}, Admin ID: {admin_id}")

    # Check if the role matches
    if role != expected_role:
        print(f"Role mismatch: Expected '{expected_role}', but found '{role}'. Access denied.")
        logger.warning(f"Invalid role access attempt. Expected: {expected_role}, Found: {role}")
        return False

    # If the role is "admin", verify admin details
    if role == "admin":
        if not admin_id:
            print("Admin ID missing from session. Access denied.")
            logger.warning("Admin ID missing from session.")
            return False

        try:
            admin = Admin.objects.get(adminid=admin_id)
            print(f"Admin found: ID={admin.adminid}, Verified={admin.is_verified}, Active={admin.is_active}")

            if not admin.is_verified:
                print(f"Admin {admin_id} is not verified. Access denied.")
                logger.warning(f"Admin {admin_id} is not verified.")
                return False

            if not admin.is_active:
                print(f"Admin {admin_id} is inactive. Access denied.")
                logger.warning(f"Admin {admin_id} is inactive.")
                return False

            print(f"Admin {admin_id} has valid access.")
            return True

        except Admin.DoesNotExist:
            print(f"Admin with ID {admin_id} does not exist. Access denied.")
            logger.error(f"Admin not found: Admin ID {admin_id}")
            return False

    print("Unexpected case encountered. Defaulting to access denied.")
    return False  # Default to False if role is incorrect or session data is missing

def add_admin(request):
    """
    Initiates the admin registration flow.
    Only a verified admin (logged in with is_verified=True) can send an invitation registration link.
    """
    # Fetch session data
    adminid = request.session.get("admin_id")
    role = request.session.get("role")
    print("Session after login:", request.session.items())
    print(f"Session data at add_admin start -> Admin ID: {adminid}, Role: {role}")

    if role != "admin":
        print("Role mismatch — redirecting to login page")
        messages.error(request, "Access denied. Only verified admins can send registration links.")
        return redirect("loginpage")

    # Fetch admin record based on session ID
    try:
        existing_admin = Admin.objects.get(adminid=adminid)
        print(f"Existing admin fetched: {existing_admin}")
        print(f"Admin attributes - is_verified: {existing_admin.is_verified}, is_active: {existing_admin.is_active}, is_superuser: {existing_admin.is_superuser}")
    except Admin.DoesNotExist:
        print("Admin not found — redirecting to admin dashboard")
        messages.error(request, "Admin not found.")
        return redirect("admin_dashboard")

    # Check if the admin is verified
    if not existing_admin.is_verified:
        print(f"Admin {adminid} not verified — redirecting to admin dashboard")
        messages.error(request, "Access denied. Only verified admins can send registration links.")
        return redirect("admin_dashboard")

    # Check if the admin is active
    if not existing_admin.is_active:
        print(f"Admin {adminid} is inactive — redirecting to admin dashboard")
        messages.error(request, "Access denied. Your account is inactive.")
        return redirect("admin_dashboard")

    # Check if the admin is a superuser
    if not existing_admin.is_superuser:
        print(f"Admin {adminid} is not a superuser — redirecting to admin dashboard")
        messages.error(request, "Access denied. Only superadmins can perform this action.")
        return redirect("admin_dashboard")

    # Continue with the invitation logic after passing all checks
    print("Admin verified and authorized — proceeding to send registration link")
    if request.method == "POST":
        emailid = request.POST.get("emailid", "").strip()
        print(f"Checking if admin with email {emailid} exists")

        if Admin.objects.filter(emailid=emailid).exists():
            print(f"Admin with this email already exists — redirecting")
            messages.error(request, "An admin with this email already exists.")
            return redirect("add_admin")

        # Generate registration link with token
        signer = TimestampSigner()
        token = signer.sign(emailid)
        registration_link = request.build_absolute_uri(reverse("register_new_admin") + f"?token={token}")
        print(f"Generated registration link: {registration_link}")

        # Send the registration link via email
        send_mail(
            'Admin Registration Invitation',
            f'You have been invited to register as an admin. Click the link below to complete your registration:\n{registration_link}',
            settings.DEFAULT_FROM_EMAIL,
            [emailid],
            fail_silently=False,
        )

        print("Registration link sent successfully!")
        messages.success(request, "Registration link sent successfully!")
        return redirect("add_admin")

    return render(request, "send_admin_invite.html")



def register_new_admin(request):
    """
    Handle new admin registration via an invitation link.
    The link contains a secure token; this view verifies the token
    and then processes the admin's registration form.
    """
    token = request.GET.get("token")
    if not token:
        messages.error(request, "Invalid or missing registration token.")
        print("Debug: No token found in the URL.")
        return redirect("loginpage")

    try:
        signer = TimestampSigner()
        emailid = signer.unsign(token, max_age=86400)  # Token is valid for 24 hours
        print(f"Debug: Token unsigned successfully, email: {emailid}")
    except SignatureExpired:
        messages.error(request, "The registration link has expired.")
        print("Debug: The registration link has expired.")
        return redirect("loginpage")
    except BadSignature:
        messages.error(request, "Invalid registration link.")
        print("Debug: Invalid registration link.")
        return redirect("loginpage")

    if request.method == "POST":
        try:
            print(f"Debug: POST data received: {request.POST}")
            new_admin = Admin.objects.create(
                firstname=request.POST.get("firstname", "").strip(),
                lastname=request.POST.get("lastname", "").strip(),
                emailid=emailid,
                password=make_password(request.POST.get("password", "").strip()),
                contactnumber=request.POST.get("phone", "").strip(),
                address=request.POST.get("address", "").strip(),
                city=request.POST.get("city", "").strip(),
                state=request.POST.get("state", "").strip(),
                country=request.POST.get("country", "").strip(),
                zip_code=request.POST.get("zip_code", "").strip(),
                gender=request.POST.get("gender", "").strip().title()
            )
            print(f"Debug: New admin created with email: {emailid}")
            messages.success(request, "Admin registered successfully! Now Admin can Login.")
            return redirect("loginpage")
        except IntegrityError as e:
            print(f"Debug: IntegrityError occurred: {e}")
            messages.error(request, "A user with this email already exists.")
            return redirect("register_new_admin")
        except ValidationError as e:
            print(f"Debug: ValidationError occurred: {e}")
            messages.error(request, f"Validation error: {e}")
            return redirect("register_new_admin")
        except Exception as e:
            print(f"Debug: Unexpected error occurred: {e}")
            messages.error(request, "An unexpected error occurred.")
            return redirect("register_new_admin")
    return render(request, "register_admin.html", {"emailid": emailid})


def invite_user(request):
    """
    Allows only a verified admin (logged in) to send an invitation registration link to a user.
    """
    print("Debug: Entering invite_user view...")
    
    # Corrected session retrieval
    admin_id = request.session.get("admin_id")  # Correct key
    role = request.session.get("role")

    print(f"Session Data -> Admin ID: {admin_id}, Role: {role}")

    # Check if session exists and role is admin
    if not admin_id:
        print("Session admin_id is missing — Redirecting to login")
        messages.error(request, "Session expired. Please log in again.")
        return redirect("loginpage")

    if role != "admin":
        print(f"Role mismatch: Expected 'admin', Found '{role}' — Redirecting to login")
        messages.error(request, "Access denied. Only verified admins can send invitations.")
        return redirect("loginpage")

    # Fetch admin from the database
    try:
        existing_admin = Admin.objects.get(adminid=admin_id)
        print(f"Admin Found -> Email: {existing_admin.emailid}, Verified: {existing_admin.is_verified}, Active: {existing_admin.is_active}")
    except Admin.DoesNotExist:
        print("Admin not found in the database — Redirecting to login")
        messages.error(request, "Admin not found. Please log in again.")
        return redirect("loginpage")

    # Check if admin is verified
    if not existing_admin.is_verified or not existing_admin.is_active:
        print("Admin is not verified or inactive — Redirecting to admin dashboard")
        messages.error(request, "Only verified admins can send invitations.")
        return redirect("admin_dashboard")

    print("Admin verified — Proceeding to send invitation link")

    if request.method == "POST":
        emailid = request.POST.get("emailid", "").strip()
        print(f"Checking if a user with email {emailid} already exists...")

        if User.objects.filter(emailid=emailid).exists():
            print("User with this email already exists — Redirecting")
            messages.error(request, "A user with this email already exists.")
            return redirect("invite_user")

        # Generate a signed token for the invitation
        signer = TimestampSigner()
        token = signer.sign(emailid)
        registration_link = request.build_absolute_uri(reverse("register_new_user") + f"?token={token}")
        
        print(f"Generated Registration Link: {registration_link}")

        # Send email with invitation link
        try:
            send_mail(
                'User Registration Invitation',
                f'You have been invited to register. Click the link below to complete your registration:\n{registration_link}',
                settings.DEFAULT_FROM_EMAIL,
                [emailid],
                fail_silently=False,
            )
            print(f"Invitation email successfully sent to {emailid}")
            messages.success(request, "Invitation link sent successfully!")
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            messages.error(request, "Failed to send the invitation email. Please try again.")

        return redirect("invite_user")

    return render(request, "send_user_invite.html")



def register_new_user(request):
    """
    Page where users register after clicking the invitation link.
    """
    token = request.GET.get("token")
    if not token:
        messages.error(request, "Invalid or missing registration token.")
        return redirect("loginpage")

    try:
        signer = TimestampSigner()
        emailid = signer.unsign(token, max_age=86400)
        print("Extracted emailid:", emailid)
    except SignatureExpired:
        messages.error(request, "The registration link has expired.")
        return redirect("loginpage")
    except BadSignature:
        messages.error(request, "Invalid registration link.")
        return redirect("loginpage")

    if request.method == "POST":
        print("Form data received:", request.POST)
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        firstname = request.POST.get("firstname", "").strip()
        lastname = request.POST.get("lastname", "").strip()
        contactnumber = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        zip_code = request.POST.get("zip_code", "").strip()
        gender = request.POST.get("gender", "").strip()
        referral_code_used = request.POST.get("referral_code", "").strip()

        print(f"Received: {firstname}, {lastname}, {username}, {emailid}, {contactnumber}, {zip_code}")

        if not firstname or not lastname or not emailid or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect("register_new_user")

        if User.objects.filter(emailid=emailid).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect("register_new_user")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another one.")
            return redirect("register_new_user")

        if len(contactnumber) != 10 or not contactnumber.isdigit():
            messages.error(request, "Please enter a valid 10-digit contact number.")
            return redirect("register_new_user")

        if gender not in ['Male', 'Female']:
            messages.error(request, "Please select a valid gender (Male or Female).")
            return redirect("register_new_user")

        referred_by = None
        referral_points = 0
        if referral_code_used:
            referred_by_user = User.objects.filter(referral_code=referral_code_used).first()
            if referred_by_user:
                referred_by = referred_by_user
                referral_points = 10 
            else:
                messages.warning(request, "Invalid referral code. Registration will continue without referral.")

        try:
            user = User.objects.create(
                firstname=firstname,
                lastname=lastname,
                emailid=emailid,
                username=username,
                password=make_password(password),
                contactnumber=contactnumber,
                address=address,
                city=city,
                state=state,
                country=country,
                zip_code=zip_code,
                gender=gender,
                status="active",
                subscription="unsubscribed",
                referral_points=referral_points,
                referred_by=referred_by
            )
            print("User created:", user)
            user.referral_code = generate_referral_code(user.userid)
            user.save()

            if referred_by:
                referred_by.referral_points += 10
                referred_by.save()

            send_mail(
                'Welcome to Indore Sports!',
                f'Hi {lastname}, thank you for registering with us.',
                'saivishnutallapureddy@gmail.com',
                [emailid],
                fail_silently=False,
            )

            request.session["user_id"] = user.userid
            request.session["role"] = "user"
            messages.success(request, "Registration successful! You can now log in.")
            return redirect("loginpage")
        except Exception as e:
            print("Error saving user:", e)
            messages.error(request, "There was an error registering your account. Please try again.")
            return redirect("register_new_user")

    return render(request, "register_user.html", {"emailid": emailid})
