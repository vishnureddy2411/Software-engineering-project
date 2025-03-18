from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from .models import Membership

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

#@login_required
def confirm_new_plan_view(request, plan_name):
    """
    Handles confirmation for purchasing a new plan. Creates a new plan under the active membership.
    """
    if plan_name not in ['WEEKLY', 'MONTHLY', 'YEARLY']:
        return redirect('membership_dashboard')

    active_membership = Membership.objects.filter(user=request.user, status='Active').first()
    if request.method == 'POST':
        if 'confirm-new-plan' in request.POST:
            duration_mapping = {
                'WEEKLY': timedelta(days=7),
                'MONTHLY': timedelta(days=30),
                'YEARLY': timedelta(days=365),
            }
            start_date = active_membership.end_date + timedelta(days=1) if active_membership else now().date()
            end_date = start_date + duration_mapping[plan_name]
            Membership.objects.create(
                user=request.user,
                plan=plan_name,
                start_date=start_date,
                end_date=end_date,
                status='Pending' if active_membership else 'Active'
            )
            return redirect('membership_dashboard')

    return render(request, 'membership_confirmation.html', {
        'plan_name': plan_name,
        'active_membership': active_membership,
    })

#@login_required
def renew_membership_view(request, membership_id):
    """
    Renews the user's active membership. Checks for eligibility and confirms renewal.
    """
    membership = get_object_or_404(Membership, id=membership_id, user=request.user)
    if (membership.end_date - now().date()).days > 2:
        return render(request, 'membership_renew_error.html', {'error': "You can only renew your membership when it's within 2 days of expiration."})

    if request.method == 'POST':
        if 'confirm-renew' in request.POST:
            duration_mapping = {
                'WEEKLY': timedelta(days=7),
                'MONTHLY': timedelta(days=30),
                'YEARLY': timedelta(days=365),
            }
            membership.end_date += duration_mapping[membership.plan]
            membership.status = 'Active'
            membership.save()
            return redirect('membership_dashboard')

        elif 'new-plan' in request.POST:
            return redirect('membership_dashboard')  # Redirect to select new plans

    return render(request, 'membership_renew.html', {'membership': membership})

#@login_required
def register_membership_view(request, plan_name):
    """
    Registers the user for a membership plan and sets the appropriate start and end dates.
    """
    if plan_name not in ['WEEKLY', 'MONTHLY', 'YEARLY']:
        return redirect('membership_dashboard')

    # Calculate membership end date based on the selected plan
    duration_mapping = {
        'WEEKLY': timedelta(days=7),
        'MONTHLY': timedelta(days=30),
        'YEARLY': timedelta(days=365),
    }
    start_date = now().date()
    end_date = start_date + duration_mapping[plan_name]

    # Cancel the active membership, if any
    current_membership = Membership.objects.filter(user=request.user, status='Active').first()
    if current_membership:
        current_membership.status = 'Cancelled'
        current_membership.save()

    # Register new membership
    Membership.objects.create(
        user=request.user,
        plan=plan_name,
        start_date=start_date,
        end_date=end_date,
        status='Active'
    )
    return redirect('membership_dashboard')

#@login_required
def cancel_membership_view(request, membership_id):
    """
    Cancels the user's active or pending membership after confirmation.
    """
    membership = get_object_or_404(Membership, id=membership_id, user=request.user)

    if request.method == 'POST':
        # Perform the cancellation
        membership.status = 'Cancelled'
        membership.save()
        return redirect('membership_dashboard')  # Redirect after cancellation

    # Render confirmation page for GET requests
    return render(request, 'membership_cancel.html', {'membership': membership})



