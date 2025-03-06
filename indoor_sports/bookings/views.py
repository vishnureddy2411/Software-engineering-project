from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def book_slot(request):
    if request.method == 'POST':
        # Add booking logic here
        pass
    return render(request, 'book_slot.html')