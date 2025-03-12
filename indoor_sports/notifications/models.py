from django.db import models
from django.conf import settings  # Use AUTH_USER_MODEL for dynamic user referencing

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('Sent', 'Sent'),
        ('Received', 'Received'),
    ]

    STATUS_CHOICES = [
        ('Unread', 'Unread'),
        ('Read', 'Read'),
    ]

    # Reference to the user who owns the notification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Type of notification: Sent or Received
    notification_type = models.CharField(
        max_length=1000,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name="Notification Type"
    )
    
    # The recipient email, optional for received notifications
    recipient_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Recipient Email"
    )
    
    # Subject of the notification or email
    subject = models.CharField(
        max_length=255,
        verbose_name="Subject"
    )
    
    # Message body of the notification or email
    message = models.TextField(
        verbose_name="Message Body"
    )
    
    # Status of the notification: Read or Unread
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Unread',
        verbose_name="Read/Unread Status"
    )
    
    # Timestamp of creation
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    # Timestamp of the last update
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    def __str__(self):
        return f"{self.notification_type} Notification - {self.subject}"

    def mark_as_read(self):
        """
        Marks the notification as read if it is unread.
        """
        if self.status == 'Unread':
            self.status = 'Read'
            self.save()

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
