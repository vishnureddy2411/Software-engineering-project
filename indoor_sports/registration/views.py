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

        messages.success(request, "Registration successful! Redirecting to your dashboard.")
        return redirect("loginpage")

    return render(request, "register_user.html")


def add_admin(request):
    """
    Initiate the admin registration flow.
    Only a verified admin (logged in) can send an invitation registration link.
    """
    print("Debug: Entering add_admin view...")
    admin_id = request.session.get("user_id")
    role = request.session.get("role")
    print(f"Session data -> Admin ID: {admin_id}, Role: {role}")

    if role != "admin":
        print("Role mismatch — redirecting to login page")
        messages.error(request, "Access denied. Only verified admins can send registration links.")
        return redirect("loginpage")

    existing_admin = Admin.objects.filter(adminid=admin_id).first()
    print(f"Existing admin -> {existing_admin}")

    if not existing_admin:
        print("Admin not found — redirecting to admin dashboard")
        messages.error(request, "Admin not found.")
        return redirect("admin_dashboard")

    if not existing_admin.is_verified:
        print("Admin not verified — redirecting to admin dashboard")
        messages.error(request, "Only verified admins can send registration links.")
        return redirect("admin_dashboard")

    print("Admin verified — proceeding to send registration link")

    if request.method == "POST":
        emailid = request.POST.get("emailid", "").strip()
        print(f"Checking if admin with email {emailid} exists")

        if Admin.objects.filter(emailid=emailid).exists():
            print("Admin with this email already exists — redirecting")
            messages.error(request, "An admin with this email already exists.")
            return redirect("add_admin")

        signer = TimestampSigner()
        token = signer.sign(emailid)
        registration_link = request.build_absolute_uri(
            reverse("register_new_admin") + f"?token={token}"
        )
        print(f"Registration link: {registration_link}")

        send_mail(
            'Admin Registration Invitation',
            f'You have been invited to register as an admin. Click the link below to complete your registration:\n{registration_link}',
            settings.DEFAULT_FROM_EMAIL,
            [emailid],
            fail_silently=False,
        )

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
    admin_id = request.session.get("user_id")
    role = request.session.get("role")
    print(f"Session data -> Admin ID: {admin_id}, Role: {role}")

    if role != "admin":
        print("Role mismatch — redirecting to login page")
        messages.error(request, "Access denied. Only verified admins can send invitations.")
        return redirect("loginpage")

    existing_admin = Admin.objects.filter(adminid=admin_id).first()
    print(f"Existing admin -> {existing_admin}")

    if not existing_admin:
        print("Admin not found — redirecting to admin dashboard")
        messages.error(request, "Admin not found.")
        return redirect("admin_dashboard")

    if not existing_admin.is_verified:
        print("Admin not verified — redirecting to admin dashboard")
        messages.error(request, "Only verified admins can send invitations.")
        return redirect("admin_dashboard")

    print("Admin verified — proceeding to send invitation link")

    if request.method == "POST":
        emailid = request.POST.get("emailid", "").strip()
        print(f"Checking if user with email {emailid} exists")

        if User.objects.filter(emailid=emailid).exists():
            print("User with this email already exists — redirecting")
            messages.error(request, "A user with this email already exists.")
            return redirect("invite_user")

        signer = TimestampSigner()
        token = signer.sign(emailid)
        registration_link = request.build_absolute_uri(
            reverse("register_new_user") + f"?token={token}"
        )
        print(f"Registration link: {registration_link}")

        send_mail(
            'User Registration Invitation',
            f'You have been invited to register. Click the link below to complete your registration:\n{registration_link}',
            settings.DEFAULT_FROM_EMAIL,
            [emailid],
            fail_silently=False,
        )

        messages.success(request, "Invitation link sent successfully!")
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
