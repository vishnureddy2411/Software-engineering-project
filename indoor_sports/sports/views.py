from django.shortcuts import render
from .models import Sport

def sport_list(request):
    sports = Sport.objects.all()
    return render(request, 'sports/sport_list.html', {'sports': sports})
