from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email(notification_type, recipient_email, context, subject=None, template_path=None):
    try:
        # Dynamically set the subject and template based on the email type
        if notification_type == "referral":
            subject = subject or "You're Invited to Join Indoor Sports Academy!"
            template_path = template_path or "emails/referral_email.html"
        elif notification_type == "transactional":
            subject = subject or "Transaction Details"
            template_path = template_path or "emails/transactional_email.html"
        elif notification_type == "promotional":
            subject = subject or "Exclusive Offer Just for You!"
            template_path = template_path or "emails/promotional_email.html"
        else:
            raise ValueError(f"Unhandled email type: {notification_type}")

        # Render the HTML template
        html_message = render_to_string(template_path, context)
        plain_message = strip_tags(html_message)

        # Send the email (displayed in the console)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"{notification_type.capitalize()} email displayed in the console for {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate {notification_type} email for {recipient_email}: {e}")
        return False

