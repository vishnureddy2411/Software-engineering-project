from django.shortcuts import render, redirect
from .models import Equipment

def equipment_list(request):
    equipment_items = Equipment.objects.all()
    return render(request, 'equipment_list.html', {'equipment_items': equipment_items})