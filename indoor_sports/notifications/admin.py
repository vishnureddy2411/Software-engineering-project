from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'user', 'status', 'created_at')  # Adjusted to valid fields
    list_filter = ('status', 'created_at')  # Removed invalid 'notification_type'
    search_fields = ('notification_type', 'message')  # Adjusted to valid fields
    ordering = ('-created_at',)
