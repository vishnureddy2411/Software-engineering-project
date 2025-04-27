
import datetime
import json
from venv import logger
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, User
from bookings.models import Booking, Slot
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from django.utils.timezone import now
from decimal import Decimal
from datetime import datetime, timezone
from django.utils.timezone import make_aware

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


# Confirm the booking and proceed to the payment page
def confirm_booking(request, slot_id):
    slot = get_object_or_404(Slot, pk=slot_id)
    if slot.is_booked:
        messages.error(request, "This slot is no longer available. Please select another slot.")
        return redirect("choose_date", location_id=slot.location.pk, sport_id=slot.sport.pk)
    
    if request.method == "POST":
        # Create the booking without any equipment or quantity details.
        booking = Booking.objects.create(
            user=request.user,
            sport=slot.sport,
            slot=slot,
            location=slot.location,
            status="Booked",
            time_slot=slot.time
        )
        slot.is_booked = True
        slot.save()
        logger.info("User %s confirmed booking %s for slot %s", request.user.username, booking.booking_id, slot)
        messages.success(request, "Your booking has been confirmed! Please proceed with payment.")
        # Redirect to payment page where payment can be made
        return redirect("payments_page", booking_id=booking.booking_id)
    
    return render(request, "confirm_booking.html", {"slot": slot})


@login_required
def process_payment(request, booking_id):
    """
    Processes Stripe Checkout session for payment, dynamically adjusting for slot-only or equipment-based pricing,
    and applying referral point discounts.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id)
    user = booking.user

    # Calculate the base price for the slot
    current_time = datetime.now().time()
    if booking.sport.peak_hours_start and booking.sport.peak_hours_end:
        if booking.sport.peak_hours_start <= current_time <= booking.sport.peak_hours_end:
            base_price = Decimal(booking.sport.peak_price)  # Peak price
        else:
            base_price = Decimal(booking.sport.price)  # Regular price
    else:
        base_price = Decimal(booking.sport.price)  # Default price

    # Determine total cost (slot price + optional equipment price)
    total_cost = base_price  # Start with slot price
    equipment_price = Decimal(0)
    if booking.equipment and booking.quantity:
        equipment_price = Decimal(booking.equipment.price) * Decimal(booking.quantity)
        total_cost += equipment_price  # Add equipment price if applicable

    # Apply referral discount (10 referral points = $1)
    points_used = min(user.referral_points, int(total_cost * 10))  # Max points usable
    discount_amount = Decimal(points_used) / 10  # Convert points to dollar discount
    final_price = max(total_cost - discount_amount, Decimal(0))  # Ensure non-negative price

    # Deduct referral points
    if points_used > 0:
        user.referral_points -= points_used
        user.save()

    # Convert final price to cents for Stripe
    amount_in_cents = int(final_price * 100)

    if request.method == "POST":
        try:
            # Create Stripe Checkout session
            session = stripe.checkout.Session.create(
                customer_email=request.user.email if request.user.is_authenticated else None,
                payment_method_types=["card", "apple_pay"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{booking.sport.name} - Slot {booking.slot.time}" +
                                    (f" + Equipment: {booking.equipment.name}" if booking.equipment else "")
                        },
                        "unit_amount": amount_in_cents,  # Final price after referral discount
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=request.build_absolute_uri(reverse('payment_success', kwargs={'booking_id': booking.booking_id})) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('payment_failed')),
            )

            # Return the session ID along with discount details
            return JsonResponse({
                "id": session.id,
                "final_price": float(final_price),
                "discount": float(discount_amount),
                "equipment_price": float(equipment_price),
            })

        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return JsonResponse({"error": "Payment processing failed", "details": str(e)}, status=400)

    return render(request, 'payments.html', {
        'booking': booking,
        'total_price': final_price,  # Final price displayed
        'equipment_price': equipment_price,  # Optional equipment price
        'discount': discount_amount,  # Discount applied
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    })

@csrf_exempt
def process_card_payment(request, booking_id):
    """Handles direct card payments using Stripe PaymentIntent, applying referral points discount before payment"""
    if request.method == "POST":
        try:
            # Parse the data from the request body
            data = json.loads(request.body)
            payment_method_id = data.get("payment_method_id")  # From frontend

            # Retrieve booking and amount
            booking = get_object_or_404(Booking, booking_id=booking_id)
            user = booking.user
            total_cost = booking.sport.price  # Total cost of the booking

            # Calculate referral points discount (10 points = 1 USD)
            points_used = min(user.referral_points, total_cost * 10)  # Max discount possible
            discount_amount = points_used / 10  # Convert points to USD
            final_price = total_cost - Decimal(discount_amount)  # Final price after applying discount

            # Deduct the referral points from the user's account
            user.referral_points -= points_used
            user.save()

            # Ensure that the minimum payment is $0.50
            if final_price < 0.50:
                return JsonResponse({'success': False, 'error': 'Minimum payment is $0.50'}, status=400)

            # Create PaymentIntent on Stripe for the final discounted price
            payment_intent = stripe.PaymentIntent.create(
                amount=int(final_price * 100),  # Convert final price to cents
                currency="usd",
                payment_method=payment_method_id,
                confirm=True,
                return_url=request.build_absolute_uri(reverse('payment_success', kwargs={'booking_id': booking.booking_id})),
            )

            # Create a payment record in the database
            Payment.objects.create(
                user=request.user,
                booking=booking,
                amount=final_price,  # Store the discounted price
                payment_method="Card",
                payment_status="Success",
                stripe_payment_id=payment_intent.id
            )

            # Return the client_secret to the frontend for confirmation
            return JsonResponse({"success": True, "client_secret": payment_intent.client_secret})

        except stripe.error.CardError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

        except stripe.error.InvalidRequestError as e:
            return JsonResponse({"success": False, "error": "Stripe request error: " + str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)



@login_required
def payment_success(request, booking_id):
    """
    Handles slot booking payment success, applies referral points discount, and updates notifications.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id)
    user = booking.user
    total_cost = booking.sport.price  # Assuming `price` field exists in Booking

    # Calculate discount based on referral points (10 points = $1)
    points_used = min(user.referral_points, (total_cost * 10))  # Max discount possible
    discount_amount = points_used / 10
    final_price = total_cost - Decimal(discount_amount)  # Use the final price after discount

    # Deduct the referral points
    user.referral_points -= points_used
    user.save()

    # Update booking status
    booking.status = 'booked'
    booking.sport.price = final_price  # Save the discounted price
    booking.save()

    # Send payment confirmation email (modify function if needed)
    send_payment_email(booking)  # Pass final_price and discount_amount to the email function

    # Insert Payment Notification
    Notification.objects.create(
        notification_type="Received",
        recipient_email=user.emailid,
        subject="Slot Booking Payment Confirmation",
        message=f"Your payment for booking ID {booking_id} has been received. {discount_amount:.2f} USD discount applied using referral points. Final amount paid: {final_price:.2f} USD.",
        status="sent",
        created_at=now(),
        updated_at=now(),
        user_id=user.userid
    )

    return render(request, "payment_success.html", {"booking": booking, "final_price": final_price, "discount": discount_amount})


def send_payment_email(booking):
    subject = f"Payment Successful for Booking {booking.booking_id}"
    message = f"Dear {booking.user.firstname},\n\nYour payment for the booking of {booking.sport.name} at {booking.location.name} on {booking.date} has been successfully processed.\n\nBooking ID: {booking.booking_id}\nSlot: {booking.time_slot}\n\nThank you for using our service!\n\nBest Regards,\nIndoor Sports Team"
    from_email = settings.DEFAULT_FROM_EMAIL  # This should be configured in your settings.py
    recipient_list = [booking.user.emailid]

    send_mail(subject, message, from_email, recipient_list)


# # Handles failed payments
def payment_failed(request):
    """Handles failed payments"""
    return render(request, 'payment_failed.html')


# Handles errors during payment processing
def error_page(request):
    """Handles errors during payment processing"""
    return render(request, 'error_page.html')


# Renders the payment selection page
def payments_page(request, booking_id):
    """Renders the payment selection page"""
    booking = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, "payments.html", {
        "booking": booking,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    })


def admin_view_payments(request):
    """
    Admin view to display all payments and calculate refund eligibility.
    Refunds are eligible only if:
    - Booking status is 'Cancelled'.
    - Payment status is 'Success'.
    - Cancellation time is at least 24 hours before slot time and date.
    """
    payments = Payment.objects.all()  # Fetch all payments

    for payment in payments:
        try:
            # Get booking details linked to the payment
            booking = Booking.objects.get(booking_id=payment.booking_id)

            # Check refund eligibility criteria
            payment_status_valid = ["Success", "Completed"]
            if payment.payment_status in payment_status_valid and booking.status == "Cancelled":
                # Get slot date and time
                slot_datetime = make_aware(datetime.combine(booking.date, booking.time_slot))
                
                # Get cancellation time
                cancellation_time = booking.cancellation_time
                
                # Handle cases where cancellation_time is missing
                if cancellation_time is None:
                    payment.refund_eligible = False  # Refund not eligible
                    continue

                # Ensure timezone-awareness for cancellation time
                if cancellation_time.tzinfo is None:
                    cancellation_time = make_aware(cancellation_time)

                # Calculate time difference in hours
                time_diff = (slot_datetime - cancellation_time).total_seconds() / 3600

                # Refund eligibility check (24 hours or more difference)
                payment.refund_eligible = time_diff >= 24
            else:
                payment.refund_eligible = False  # Refund not eligible
        except Booking.DoesNotExist:
            payment.refund_eligible = False  # Refund not eligible if booking is missing

    return render(request, 'admin_view_payments.html', {'payments': payments})




def send_refund_email(booking, payment):
    """
    Sends a refund email to the user when the refund is processed.
    """
    try:
        subject = f"Refund Processed for Booking {booking.booking_id}"
        message = f"""Dear {booking.user.firstname},

Your refund for the booking of {booking.sport.name} at {booking.location.name} on {booking.date} has been approved.
You will receive the amount of ${payment.amount} within 3 business days.

Booking ID: {booking.booking_id}
Slot: {booking.time_slot}

Thank you for using our service, and we hope to serve you again in the future!

Best Regards,
Indoor Sports Team
"""
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [booking.user.emailid]  # Ensure 'emailid' is correctly set in your User model

        # Send email
        send_mail(subject, message, from_email, recipient_list)
        print(f"Refund email successfully sent to {booking.user.emailid}")
    except Exception as e:
        print(f"Failed to send refund email: {e}")

def process_refund(request, id):
    """
    Processes refunds for eligible payments.
    Refunds are processed only if:
    - Booking status is 'Cancelled'.
    - Payment status is 'Success'.
    - Cancellation time is at least 24 hours before slot time and date.
    """
    payment = get_object_or_404(Payment, id=id)
    booking = get_object_or_404(Booking, booking_id=payment.booking_id)

    if payment.payment_status in ["Success", "Completed"] and booking.status == "Cancelled":
        # Combine slot date and time into a single datetime object
        slot_datetime = make_aware(datetime.combine(booking.date, booking.time_slot))
        
        # Ensure cancellation time is present and timezone-aware
        cancellation_time = booking.cancellation_time
        if cancellation_time is None:
            messages.error(request, "Refund not possible as cancellation time is missing.")
            return redirect('admin_view_payments')

        if cancellation_time.tzinfo is None:
            cancellation_time = make_aware(cancellation_time)

        # Calculate time difference in hours
        time_diff = (slot_datetime - cancellation_time).total_seconds() / 3600

        # Refund eligibility check
        if time_diff >= 24:
            payment.payment_status = "Refunded"
            payment.save()

            # Send refund email to the user
            send_refund_email(booking, payment)

            # Notify admin of successful refund
            messages.success(request, f"Refund for Payment ID {payment.id} processed successfully.")
        else:
            messages.error(request, "Refund not eligible as cancellation did not occur 24 hours before the slot time.")
    else:
        messages.error(request, "Refund not possible for this payment.")

    return redirect('admin_view_payments')

