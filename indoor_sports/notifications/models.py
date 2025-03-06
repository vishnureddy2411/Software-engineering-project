from django.db import models
from accounts.models import User

class Notification(models.Model):
    NOTIFICATION_STATUS_CHOICES = [
        ('Unread', 'Unread'),
        ('Read', 'Read'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)  # e.g., Booking Confirmation, Cancellation, Reminder
    message = models.TextField()
    status = models.CharField(max_length=10, choices=NOTIFICATION_STATUS_CHOICES, default='Unread')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification {self.id} for {self.user.email}"
