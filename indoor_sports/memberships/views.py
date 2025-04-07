from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from .models import Membership
import stripe
from django.conf import settings
from notifications.models import Notification
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail

stripe.api_key = settings.STRIPE_SECRET_KEY
#@login_required
def membership_dashboard_view(request):
    """
    Displays the membership dashboard with active membership, upcoming plans, and available plans.
    """
    active_membership = Membership.objects.filter(user=request.user, status='Active').first()
    user_memberships = Membership.objects.filter(user=request.user).exclude(status='Cancelled')
    available_plans = [
        {'name': 'WEEKLY', 'duration': '7 Days', 'price': 10.0},
        {'name': 'MONTHLY', 'duration': '30 Days', 'price': 30.0},
        {'name': 'YEARLY', 'duration': '365 Days', 'price': 300.0},
    ]
    return render(request, 'membership_dashboard.html', {
        'active_membership': active_membership,
        'user_memberships': user_memberships,
        'available_plans': available_plans,
    })



@login_required
def confirm_new_plan_view(request, plan):
    """Handles confirmation for purchasing a new plan. Creates a new plan under the active membership."""
    if plan not in ['WEEKLY', 'MONTHLY', 'YEARLY']:
        return redirect('membership_dashboard')

    active_membership = Membership.objects.filter(user=request.user, status='Active').first()
    
    if request.method == 'POST' and 'confirm-new-plan' in request.POST:
        duration_mapping = {
            'WEEKLY': timedelta(days=7),
            'MONTHLY': timedelta(days=30),
            'YEARLY': timedelta(days=365),
        }
        start_date = active_membership.end_date + timedelta(days=1) if active_membership else now().date()
        end_date = start_date + duration_mapping[plan]
        Membership.objects.create(
            user=request.user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='Pending' if active_membership else 'Active'
        )
        return redirect('membership_dashboard')

    return render(request, 'membership_confirmation.html', {
        'plan': plan,
        'active_membership': active_membership,
    })


@login_required
def renew_membership_view(request, membership_id):
    """Renews the user's active membership. Checks for eligibility and confirms renewal."""
    membership = get_object_or_404(Membership, id=membership_id, user=request.user)
    
    if (membership.end_date - now().date()).days > 2:
        return render(request, 'membership_renew_error.html', {
            'error': "You can only renew your membership when it's within 2 days of expiration."
        })

    if request.method == 'POST':
        duration_mapping = {
            'WEEKLY': timedelta(days=7),
            'MONTHLY': timedelta(days=30),
            'YEARLY': timedelta(days=365),
        }

        if 'confirm-renew' in request.POST:
            membership.end_date += duration_mapping[membership.plan]
            membership.status = 'Active'
            membership.save()
            return redirect('membership_dashboard')

        elif 'new-plan' in request.POST:
            return redirect('membership_dashboard')

    return render(request, 'membership_renew.html', {'membership': membership})


@login_required
def register_membership_view(request, plan):
    """Registers the user for a membership plan and sets the appropriate start and end dates."""
    if plan not in ['WEEKLY', 'MONTHLY', 'YEARLY']:
        return redirect('membership_dashboard')

    duration_mapping = {
        'WEEKLY': timedelta(days=7),
        'MONTHLY': timedelta(days=30),
        'YEARLY': timedelta(days=365),
    }

    start_date = now().date()
    end_date = start_date + duration_mapping[plan]

    current_membership = Membership.objects.filter(user=request.user, status='Active').first()
    if current_membership:
        current_membership.status = 'Cancelled'
        current_membership.save()

    Membership.objects.create(
        user=request.user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        status='Active'
    )
    return redirect('membership_dashboard')


@login_required
def cancel_membership_view(request, membership_id):
    """Cancels the user's active or pending membership after confirmation."""
    membership = get_object_or_404(Membership, id=membership_id, user=request.user)

    if request.method == 'POST':
        membership.status = 'Cancelled'
        membership.save()
        return redirect('membership_dashboard')

    return render(request, 'membership_cancel.html', {'membership': membership})


@login_required
def create_checkout_session(request, plan):
    """Create Stripe Checkout session for the subscription plan"""

    price_mapping = {
        'WEEKLY': 'price_1R8pYGAzH5PP5Ex8N9IIAL5c',
        'MONTHLY': 'price_1R8pNjAzH5PP5Ex8msvzQvUp',
        'YEARLY': 'price_1R8pZFAzH5PP5Ex8gFOuqKB0',
    }

    if plan not in price_mapping:
        return redirect('membership_dashboard')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_mapping[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('subscription_payment_success', kwargs={'plan': plan})) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('subscription_payment_cancel')),
        )

        return redirect(session.url, code=303)

    except stripe.error.StripeError as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('membership_dashboard')


@login_required
def subscription_payment_success(request, plan):
    """Handles subscription payment success and updates notifications."""
    price_mapping = {
        'WEEKLY': 10.0,
        'MONTHLY': 30.0,
        'YEARLY': 300.0,
    }

    duration_mapping = {
        'WEEKLY': timedelta(weeks=1),
        'MONTHLY': timedelta(days=30),
        'YEARLY': timedelta(days=365),
    }

    start_date = now().date()
    end_date = start_date + duration_mapping.get(plan, timedelta(weeks=1))
    price = price_mapping.get(plan, 0)

    subscription = Membership.objects.create(
        user=request.user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        price=price,
        status='Active',
    )

    subscription_send_payment_email(request.user, plan, start_date, end_date, price)

    Notification.objects.create(
        notification_type="Payment Received",
        recipient_email=request.user.emailid,
        subject="Subscription Payment Confirmation",
        message=f"We have received your payment for the {plan} subscription. Your subscription is active from {start_date} to {end_date}.",
        status="sent",
        created_at=now(),
        updated_at=now(),
        user_id=request.user.userid
    )

    messages.success(request, f"Your {plan} subscription has been successfully activated!")

    return render(request, 'mem_payment_success.html', {
        'plan': plan,
        'start_date': start_date,
        'end_date': end_date,
        'price': price,
    })


def subscription_payment_cancel(request):
    """Handles failed payments"""
    return render(request, 'mem_payment_failed.html')


def subscription_send_payment_email(user, plan, start_date, end_date, price):
    subject = f"Subscription Payment Successful for {plan} Plan"
    message = (
        f"Dear {user.username},\n\n"
        f"Your payment for the {plan} subscription plan has been successfully processed.\n\n"
        f"Plan: {plan}\n"
        f"Start Date: {start_date}\n"
        f"End Date: {end_date}\n"
        f"Amount: ${price}\n\n"
        f"Thank you for subscribing!\n\n"
        f"Best Regards,\nThe Team"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.emailid]
    send_mail(subject, message, from_email, recipient_list)
