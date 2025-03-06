# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Booking
from ..notificati.models import Notification  # assuming Notification model lives in notifications/models.py

@receiver(post_save, sender=Booking)
def create_booking_notification(sender, instance, created, **kwargs):
    if created:
        # Create a notification when a booking is created.
        Notification.objects.create(
            user=instance.user,  # the user who made the booking
            notification_type='Booking Confirmation',
            message=f"Your booking with ID {instance.id} has been confirmed.",
        )
