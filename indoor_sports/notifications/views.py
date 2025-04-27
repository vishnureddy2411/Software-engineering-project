from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

@login_required
def email_list_view(request):
    """
    Displays sent and received notifications (emails) for the logged-in user.
    """
    sent_emails = Notification.objects.filter(user=request.user, notification_type='Sent').order_by('-created_at')
    received_emails = Notification.objects.filter(user=request.user, notification_type='Received').order_by('-created_at')
    unread_count = received_emails.filter(status='Unread').count()

    return render(request, 'email_list.html', {
        'sent_emails': sent_emails,
        'received_emails': received_emails,
        'unread_count': unread_count,
    })


@login_required
def email_detail_view(request, email_id):
    """
    Displays the details of a notification (email) and marks it as read if it is received.
    """
    email = get_object_or_404(Notification, id=email_id, user=request.user)

    # Mark as read if it is a received email and unread
    if email.notification_type == 'Received' and email.status == 'Unread':
        email.status = 'Read'
        email.save()

    return render(request, 'email_detail.html', {'email': email})


@login_required
def mark_all_as_read(request):
    """
    Marks all received notifications (emails) as read.
    """
    Notification.objects.filter(user=request.user, notification_type='Received', status='Unread').update(status='Read')
    return redirect('email_list')


@login_required
def send_email_to_customer_service(request):
    """
    Allows users to send emails to customer service.
    """
    if request.method == 'POST':
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        customer_service_email = settings.CUSTOMER_SERVICE
 
        if subject and body:
            # Sending the email
            send_mail(
                subject=subject,
                message=body,
                from_email=request.user.emailid,
                recipient_list=[customer_service_email],
                fail_silently=False,
            )
 
            # Saving the sent email as a notification in the database
            Notification.objects.create(
                user=request.user,
                notification_type='Sent',
                recipient_email=customer_service_email,
                subject=subject,
                message=body,
                status='Read'  # Sent emails are marked as Read by default
            )
 
            return redirect('email_list')
 
    return render(request, 'send_email.html')
 
 