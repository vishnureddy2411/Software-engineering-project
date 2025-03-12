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
import logging

logger = logging.getLogger(__name__)

@login_required
def my_referrals(request):
    referral_code = request.user.referral_code or "N/A"
    #referral_link = request.build_absolute_uri(f"/register?referral_code={referral_code}")
    referral_link = request.build_absolute_uri("/")

    referrals = User.objects.filter(referred_by=request.user).order_by("-date_joined")

    if request.method == "POST":
        friend_email = request.POST.get("friend_email", "").strip()
        if not friend_email:
            messages.error(request, "Please provide a valid email address.")
        else:
            try:
                validate_email(friend_email)

                # Check if the user already exists
                if User.objects.filter(email=friend_email).exists():
                    messages.info(request, f"{friend_email} is already registered with Indoor Sports Academy.")
                else:
                    # Create the email content
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
                        from_email='admin@indoorsportsacademy.com',
                        recipient_list=[friend_email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    # Log notification
                    Notification.objects.create(
                        user=request.user,
                        notification_type="Referral Email Sent",
                        message=f"Referral email sent to {friend_email} with code {referral_code}",
                    )

                    messages.success(request, f"Referral email sent to {friend_email}.")
            except ValidationError:
                messages.error(request, "Invalid email address.")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                messages.error(request, "Failed to send referral email. Please try again later.")

    return render(request, "my_referrals.html", {
        "referral_code": referral_code,
        "referral_link": referral_link,
        "referrals": referrals,
    })
