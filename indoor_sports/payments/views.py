
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
        notification_type="Payment Received",
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


