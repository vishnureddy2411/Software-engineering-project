from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification  # Updated to use the Notification model

@receiver(post_save, sender=Notification)
def create_notification_for_received_email(sender, instance, created, **kwargs):
    """
    Automatically creates a notification entry for received emails.
    """
    if created and instance.notification_type == 'Received':
        # Example logic for creating a related notification
        instance.user.notifications.create(
            notification_type="New Email Received",
            message=f"You have a new email: {instance.subject}",
        )