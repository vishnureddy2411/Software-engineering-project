from .models import Notification

def unread_notifications_count(request):
    """
    Context processor to count unread notifications for the logged-in user.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            notification_type='Received',
            status='Unread'
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
