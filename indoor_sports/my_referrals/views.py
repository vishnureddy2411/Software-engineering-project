from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from notifications.models import Notification
from accounts.models import User
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)

# @login_required(login_url="loginpage")
def my_referrals(request):
    """
    Displays user's referrals and allows referral emails to be sent.
    """
    # Debug: Log session and user info
    logger.info("Accessing my_referrals. User: %s, Authenticated: %s", request.user, request.user.is_authenticated)

    if not request.user.is_authenticated:
        logger.error("User is not authenticated!")
        return redirect("loginpage")

    # Retrieve the referral code from the logged-in user (or use "N/A" if not set)
    referral_code = getattr(request.user, "referral_code", "N/A")
    referral_link = request.build_absolute_uri("/") + "?ref=" + referral_code  # Update as necessary

    # Fetch referrals ordered by created_at (descending)
    try:
        referrals = User.objects.filter(referred_by=request.user).order_by("-createdat")
        logger.info("Retrieved %d referrals for user %s", referrals.count(), request.user)
    except Exception as e:
        logger.error("Error fetching referrals: %s", e)
        referrals = []

    if request.method == "POST":
        friend_email = request.POST.get("friend_email", "").strip()
        if not friend_email:
            messages.error(request, "Please provide a valid email address.")
        else:
            try:
                validate_email(friend_email)  # Validate email format
                
                # Check if the email is already registered using the 'emailid' field
                if User.objects.filter(emailid=friend_email).exists():
                    messages.info(request, f"{friend_email} is already registered with Indoor Sports Academy.")
                else:
                    # Prepare email context 
                    context = {
                        "username": request.user.username,
                        "referral_code": referral_code,
                        "referral_link": referral_link,
                    }
                    html_message = render_to_string("referral_email.html", context)
                    plain_message = strip_tags(html_message)

                    # Send the referral email
                    send_mail(
                        subject="You're Invited to Join Indoor Sports Academy!",
                        message=plain_message,
                        from_email="admin@indoorsportsacademy.com",
                        recipient_list=[friend_email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    # Log the notification
                    Notification.objects.create(
                        user=request.user,
                        notification_type="Referral Email Sent",
                        message=f"Referral email sent to {friend_email}.",
                    )
                    
                    messages.success(request, f"Referral email sent to {friend_email}.")
                    logger.info("Referral email sent successfully to %s", friend_email)
            except ValidationError:
                messages.error(request, "Invalid email address.")
                logger.warning("ValidationError for friend_email: %s", friend_email)
            except Exception as e:
                logger.error("Failed to send referral email: %s", e)
                messages.error(request, "Failed to send referral email. Please try again later.")

    return render(request, "my_referrals.html", {
        "referral_code": referral_code,
        "referral_link": referral_link,
        "referrals": referrals,
    })

@login_required(login_url="loginpage")
def logout_view(request):
    """
    Logs out the user/admin and clears all session data.
    """
    logger.info("Logging out user. Session before flush: %s", request.session.items())
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("loginpage")
