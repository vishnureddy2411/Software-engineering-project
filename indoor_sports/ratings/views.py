from django.shortcuts import render, redirect
from .models import Review

def give_rating(request):
    if request.method == 'POST':
        # Logic for submitting rating
        pass
    return render(request, 'give_rating.html')