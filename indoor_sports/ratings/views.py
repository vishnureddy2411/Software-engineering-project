from django.contrib.admin.views.decorators import staff_member_required 
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib import messages
from django.db.models import Avg
from ratings.models import Review
from bookings.models import Booking
from sports.models import Location, Sport
 
def rating_based_on_location(request, location_id, sport_id, booking_id=None):
    # Fetch the related sport and location objects using their correct primary key fields
    sport = get_object_or_404(Sport, sport_id=sport_id)  # Use `sport_id`
    location = get_object_or_404(Location, location_id=location_id)  # Use `location_id`
 
    print("Here is the review for the location:", location.name)
 
    if request.method == 'POST':
        # Get the rating and review text from the POST request
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
 
        # Debugging input values
        print(f"Rating: {rating}, Review Text: {review_text}")
 
        if rating and review_text:
            try:
                # Ensure rating is an integer
                rating = int(rating)
 
                # 1. Save the rating to the ratings_review table
                Review.objects.create(
                    user_id=request.user.userid,  # Use `userid` instead of `id`
                    sport_id=sport.sport_id,  # Associate with the sport
                    location_id=location.location_id,  # Associate with the location
                    rating=rating,  # Save the rating
                    review_text=review_text,  # Store the review text
                    created_at=now()  # Set the current timestamp
                )
                print("Review saved successfully in the reviews table.")
 
                # 2. Update submitted_review in the bookings_booking table
                if booking_id is not None:
                    booking_updated = Booking.objects.filter(booking_id=booking_id).update(submitted_review=True)
                    if booking_updated:
                        print(f"Booking ID {booking_id}: submitted_review updated successfully.")
                    else:
                        print(f"Booking ID {booking_id} not found in the bookings table.")
 
                messages.success(request, "Thank you for your review!")
                return redirect('reviews_by_location', location_id=location_id, sport_id=sport_id)
 
            except ValueError:
                print("Invalid rating format. Rating must be a number.")
                messages.error(request, "Rating must be a valid number.")
            except Exception as e:
                print(f"Failed to save review: {str(e)}")
                messages.error(request, "Failed to save the review. Please try again.")
 
    # Fetch reviews and calculate the average rating
    reviews = Review.objects.filter(sport_id=sport.sport_id, location_id=location.location_id).order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
 
    return render(request, 'reviews.html', {
        'sport': sport,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
    })
 
def show_reviews(request, location_id, sport_id):
    sport = get_object_or_404(Sport, sport_id=sport_id)
    location = get_object_or_404(Location, location_id=location_id)
    print("here is the review for the location", location.name)
 
    reviews = Review.objects.filter(sport=sport, location=location).order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
 
    return render(request, 'reviews.html', {
        'sport': sport,
        'reviews': reviews,
        'average_rating': round(average_rating, 1)
    })
 
 
 
 
 
def give_rating(request, sport_id, location_id):
 
    sport = get_object_or_404(Sport, sport_id=sport_id)
 
    location = get_object_or_404(Location, location_id=location_id)
 
    if request.method == 'POST':
 
        rating = request.POST.get('rating')
 
        review_text = request.POST.get('review_text')
 
        if rating and review_text:
 
            try:
 
                Review.objects.create(
 
                    user=request.user,
 
                    sport=sport,
 
                    location=location,
 
                    rating=rating,
 
                    review_text=review_text
 
                )
 
                messages.success(request, "Thanks for your review!")
 
                return redirect('reviews_by_location', location_id=location_id, sport_id=sport_id)
 
            except Exception as e:
 
                print("Review creation failed:", e)
 
                messages.error(request, "Something went wrong while saving your review.")
 
        else:
 
            messages.warning(request, "Please fill both rating and review text.")
 
    reviews = Review.objects.filter(sport=sport, location=location).order_by('-created_at')
 
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
 
    return render(request, 'reviews.html', {
 
        'sport': sport,
 
        'location': location,
 
        'reviews': reviews,
 
        'average_rating': round(average_rating, 1)
 
    })
 
 
def admin_reviews(request):
    reviews = Review.objects.select_related('user', 'sport').values(
        'user__username',  # Get username from the related user model
        'sport__name',     # Get name from the related sport model
        'rating',
        'review_text',
        'created_at'
    )
    return render(request, 'admin_reviews.html', {'reviews': reviews})
 