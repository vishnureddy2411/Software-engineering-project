from venv import logger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta

import stripe
from django.conf import settings
from notifications.models import Notification
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail


from accounts.models import Admin  # import your custom Admin model


from .models import Membership, MembershipPlan
from .forms import MembershipForm
from .forms import MembershipPlanForm
from django.http import HttpResponse
from payments.models import MembershipPayment
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def membership_dashboard_view(request):
    active_membership = Membership.objects.filter(user=request.user, status='Active').first()
    user_memberships = Membership.objects.filter(user=request.user).exclude(status='Cancelled')
    available_plans = MembershipPlan.objects.all()

    return render(request, 'membership_dashboard.html', {
        'active_membership': active_membership,
        'user_memberships': user_memberships,
        'available_plans': available_plans,
    })

@login_required
def confirm_new_plan_view(request, plan_id):
    membership_plan = get_object_or_404(MembershipPlan, id=plan_id)
    active_membership = Membership.objects.filter(user=request.user, status='Active').first()

    if request.method == 'POST' and 'confirm-new-plan' in request.POST:
        # Redirect to Stripe payment
        return redirect(reverse('create_checkout_session', kwargs={'plan': membership_plan.name}))

    return render(request, 'membership_confirmation.html', {
        'plan_name': membership_plan.name,
        'active_membership': active_membership,
    })


@login_required
def renew_membership_view(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id, user=request.user)

    if (membership.end_date - now().date()).days > 2:
        return render(request, 'membership_renew_error.html', {
            'error': "You can only renew your membership when it's within 2 days of expiration."
        })

    if request.method == 'POST' and 'confirm-renew' in request.POST:
        plan = membership.plan
        membership.end_date += timedelta(days=int(plan.duration))
        membership.status = 'Active'
        membership.save()
        messages.success(request, "Membership renewed successfully.")
        return redirect('membership_dashboard')

    return render(request, 'membership_renew.html', {'membership': membership})

@login_required
def register_membership_view(request, plan_id):
    membership_plan = get_object_or_404(MembershipPlan, id=plan_id)
    start_date = now().date()
    end_date = start_date + timedelta(days=int(membership_plan.duration))

    current_membership = Membership.objects.filter(user=request.user, status='Active').first()
    if current_membership:
        current_membership.status = 'Cancelled'
        current_membership.save()

    Membership.objects.create(
        user=request.user,
        plan_id=membership_plan.id,
        start_date=start_date,
        end_date=end_date,
        status='Active',
        price=membership_plan.price,
    )
    return redirect('membership_dashboard')

@login_required
def cancel_membership_view(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id, user=request.user)

    if request.method == 'POST':
        membership.status = 'Cancelled'
        membership.save()
        return redirect('membership_dashboard')

    return render(request, 'membership_cancel.html', {'membership': membership})

STRIPE_PRICE_MAPPING = {
    "Silver": "price_1RHqlGAzH5PP5Ex8P6WV6oDL",
    "Gold": "price_1RHqnDAzH5PP5Ex8twjG11UO",
    "Platinum": "price_1RHqoeAzH5PP5Ex8ocPRHHtU",
}


@login_required
def create_checkout_session(request, plan):
    stripe_price_id = STRIPE_PRICE_MAPPING.get(plan)  # Get Stripe price ID from mapping

    if not stripe_price_id:
        messages.error(request, "Invalid membership plan selected.")
        return redirect('membership_dashboard')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(
                reverse('subscription_payment_success', kwargs={'plan_duration': plan})
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('subscription_payment_cancel')),
        )
        return redirect(session.url, code=303)
    except stripe.error.StripeError as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('membership_dashboard')


DURATION_MAPPING = {
    'Weekly': 7,
    'Monthly': 30,
    'Yearly': 365,
}

# @login_required
# def subscription_payment_success(request, plan_duration):
#     """
#     Handles successful subscription payments and activates the membership.
#     """
#     # Get the MembershipPlan by name (e.g., "Gold", "Silver", "Platinum")
#     membership_plan = get_object_or_404(MembershipPlan, name=plan_duration)

#     # Map duration (e.g., "Monthly") to integer day count
#     duration_in_days = DURATION_MAPPING.get(membership_plan.duration)
#     if not duration_in_days:
#         messages.error(request, f"Invalid duration '{membership_plan.duration}' specified for the plan.")
#         return redirect('membership_dashboard')

#     # Calculate start and end dates
#     start_date = now().date()
#     end_date = start_date + timedelta(days=duration_in_days)

#     # Create the membership
#     Membership.objects.create(
#         user=request.user,
#         plan=membership_plan,
#         start_date=start_date,
#         end_date=end_date,
#         price=membership_plan.price,
#         status='Active',
#     )

#     # Send confirmation email
#     subscription_send_payment_email(
#         user=request.user,
#         plan=membership_plan.name,
#         start_date=start_date,
#         end_date=end_date,
#         price=membership_plan.price
#     )

#     # Create a notification
#     Notification.objects.create(
#         notification_type="Payment Received",
#         recipient_email=request.user.emailid,
#         subject="Subscription Payment Confirmation",
#         message=f"We have received your payment for the {membership_plan.name} subscription. "
#                 f"Your subscription is active from {start_date} to {end_date}.",
#         status="sent",
#         created_at=now(),
#         updated_at=now(),
#         user_id=request.user.userid
#     )

#     # Display success message
#     messages.success(request, f"Your {membership_plan.name} subscription has been successfully activated!")
#     return render(request, 'mem_payment_success.html', {
#         'plan': membership_plan.name,
#         'start_date': start_date,
#         'end_date': end_date,
#         'price': membership_plan.price,
#     })




@login_required

def subscription_payment_success(request, plan_duration):

    """

    Handles successful subscription payments and activates the membership.

    """

    try:

        # Get the MembershipPlan by name (e.g., "Gold", "Silver", "Platinum")

        membership_plan = get_object_or_404(MembershipPlan, name=plan_duration)
 
        # Map duration (e.g., "Weekly") to integer day count

        duration_in_days = DURATION_MAPPING.get(membership_plan.duration)

        if not duration_in_days:

            messages.error(request, f"Invalid duration '{membership_plan.duration}' specified for the plan.")

            return redirect('membership_dashboard')
 
        # Calculate start and end dates

        start_date = now().date()

        end_date = start_date + timedelta(days=duration_in_days)
 
        # Create the membership

        membership = Membership.objects.create(

            user=request.user,

            plan=membership_plan,

            start_date=start_date,

            end_date=end_date,

            price=membership_plan.price,

            status='Active',

        )
 
        # **New Logic: Store Membership Payment**

        try:

            payment = MembershipPayment.objects.create(

                user=request.user,

                plan=membership_plan,

                membership=membership,

                amount=membership_plan.price,

                payment_status='Success',

                stripe_payment_id=f"stripe_{membership.id}_{int(now().timestamp())}"  # Example Stripe ID

            )

            # Log the successful payment storage

            logger.info(f"Payment stored successfully: {payment}")

        except Exception as payment_error:

            logger.error(f"Failed to store payment: {payment_error}")
 
        # Send confirmation email

        subscription_send_payment_email(

            user=request.user,

            plan=membership_plan.name,

            start_date=start_date,

            end_date=end_date,

            price=membership_plan.price

        )
 
        # Create a notification

        Notification.objects.create(

            notification_type="Payment Received",

            recipient_email=request.user.emailid,

            subject="Subscription Payment Confirmation",

            message=f"We have received your payment for the {membership_plan.name} subscription. "

                    f"Your subscription is active from {start_date} to {end_date}.",

            status="Sent",

            created_at=now(),

            updated_at=now(),

            user_id=request.user.userid

        )
 
        # Display success message

        messages.success(request, f"Your {membership_plan.name} subscription has been successfully activated!")

        return render(request, 'mem_payment_success.html', {

            'plan': membership_plan.name,

            'start_date': start_date,

            'end_date': end_date,

            'price': membership_plan.price,

        })
 
    except Exception as e:

        # Log any exceptions that occur during the process

        logger.error(f"An error occurred during subscription payment processing: {str(e)}")
 
        # Display an error message to the user

        messages.error(request, "An error occurred while processing your subscription. Please try again.")

        return redirect('membership_dashboard')
 


 

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


# @login_required
def view_user_memberships(request):
    # Ensure only logged-in users with role 'admin' can access
    if request.session.get('role') != 'admin' or not request.session.get('is_authenticated'):
        print("Access denied: Not an admin or not authenticated.")
        messages.error(request, "Access denied. Admins only.")
        return redirect('loginpage')

    try:
        # Get admin_id from session and fetch Admin object
        admin_id = request.session.get('admin_id')
        admin = Admin.objects.get(adminid=admin_id)
        print(f"Admin fetched: {admin.emailid}")

        if not admin.is_verified:
            print("Access denied: Admin is not verified.")
            messages.error(request, "Access denied. Verified Admins only.")
            return redirect('loginpage')

        memberships = Membership.objects.select_related('user').all().order_by('-created_at')
        print(f"Membership records fetched: {len(memberships)}")

        return render(request, 'admin_membership_view.html', {
            'memberships': memberships,
            'admin': admin
        })

    except Admin.DoesNotExist:
        print("Admin not found.")
        messages.error(request, "Access denied. Admin not found.")
        return redirect('loginpage')


def update_membership(request, id):
    if request.session.get('role') != 'admin' or not request.session.get('is_authenticated'):
        print("Access denied: Not an admin or not authenticated.")
        messages.error(request, "Access denied. Admins only.")
        return redirect('loginpage')

    try:
        admin_id = request.session.get('admin_id')
        admin = Admin.objects.get(adminid=admin_id)
        print(f"Admin fetched: {admin.emailid}")

        if not admin.is_verified:
            print("Access denied: Admin is not verified.")
            messages.error(request, "Access denied. Verified Admins only.")
            return redirect('loginpage')

        membership = get_object_or_404(Membership, id=id)

        if request.method == 'POST':
            membership.plan_id = request.POST.get('plan_id')
            membership.price = request.POST.get('price')
            membership.status = request.POST.get('status')
            membership.save()

            messages.success(request, "Membership updated successfully.")
            return redirect('view_user_memberships')

        return render(request, 'membership_form.html', {
            'membership': membership,
            'admin': admin
        })

    except Admin.DoesNotExist:
        print("Admin not found.")
        messages.error(request, "Access denied. Admin not found.")
        return redirect('loginpage')

    
def membership_plan_list(request):
    plans = MembershipPlan.objects.all()
    return render(request, 'membership_plan_list.html', {'plans': plans})


def admin_dashboard(request):
    memberships = Membership.objects.select_related('plan').all()  # Preload the plan for optimization
    return render(request, 'dashboards/admin_dashboard.html', {'memberships': memberships})



def update_membership_plan(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id)

    if request.method == 'POST':
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership plan updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = MembershipPlanForm(instance=plan)

    return render(request, 'update_membership.html', {'form': form, 'plan': plan})


def delete_membership_plan(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id)

    if request.method == 'POST':
        plan.delete()
        messages.success(request, "Membership plan deleted successfully.")
        return redirect('admin_dashboard')

    return render(request, 'membership_plan/delete_membership.html', {'plan': plan})
