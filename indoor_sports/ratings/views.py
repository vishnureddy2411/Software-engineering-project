from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg

from bookings.models import Booking
from .models import Review
from sports.models import Location, Sport


from django.contrib.admin.views.decorators import staff_member_required

def rating_based_on_location(request, location_id, sport_id, booking_id=None):
    sport = get_object_or_404(Sport, sport_id=sport_id)
    location = get_object_or_404(Location, location_id=location_id)
    print("here is the review for the location", location.name)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')

        if rating and review_text:
            Review.objects.create(
                user=request.user,
                sport=sport,
                location=location,
                rating=rating,
                review_text=review_text
            )
            if booking_id is not None:
                Booking.objects.filter(booking_id=booking_id).update(submitted_review=True)

            return redirect('reviews_by_location', location_id=location_id, sport_id=sport_id)

    reviews = Review.objects.filter(sport=sport, location=location).order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    return render(request, 'reviews.html', {
        'sport': sport,
        'reviews': reviews,
        'average_rating': round(average_rating, 1)
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


def give_rating(request, sport_id):
    sport = get_object_or_404(Sport, sport_id=sport_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')

        if rating and review_text:
            Review.objects.create(
                user=request.user,
                sport=sport,
                rating=rating,
                review_text=review_text
            )
            return redirect('reviews_by_location', location_id=0, sport_id=sport_id)  # Adjust if location is required

    reviews = Review.objects.filter(sport=sport).order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    return render(request, 'reviews.html', {
        'sport': sport,
        'reviews': reviews,
        'average_rating': round(average_rating, 1)
    })

# def admin_reviews(request):
#     reviews = Review.objects.select_related('user', 'sport').only(
#         'user_username', 'sport_name', 'rating', 'review_text', 'created_at'
#     )
#     return render(request, 'admin_reviews.html', {'reviews': reviews})



def admin_reviews(request):
    reviews = Review.objects.select_related('user', 'sport').values(
        'user__username',  # Get username from the related user model
        'sport__name',     # Get name from the related sport model
        'rating',
        'review_text',
        'created_at'
    )
    return render(request, 'admin_reviews.html', {'reviews': reviews})