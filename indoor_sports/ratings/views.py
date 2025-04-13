# from django.shortcuts import render, redirect
# from .models import Review

# def give_rating(request):
#     if request.method == 'POST':
#         # Logic for submitting rating
#         pass
#     return render(request, 'give_rating.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Review
from sports.models import Sport

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
            return redirect('reviews', sport_id=sport.sport_id)

    reviews = Review.objects.filter(sport=sport).order_by('-created_at')  # Show existing reviews
    return render(request, 'reviews.html', {'sport': sport, 'reviews': reviews})

