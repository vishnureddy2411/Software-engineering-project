<<<<<<< HEAD
from django.shortcuts import render
from .models import Equipment

def equipment_list(request):
    equipment = Equipment.objects.all()
    return render(request, 'equipment_list.html', {'equipment': equipment})
=======
from django.urls import path
from . import views

urlpatterns = [
    path('equipment/', views.equipment_list, name='equipment_list'),
    
]

>>>>>>> 587daca803448929c1cfa1e6e31a62917d21a21d
