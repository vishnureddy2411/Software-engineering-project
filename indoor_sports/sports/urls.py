from django.urls import path
from . import views

urlpatterns = [
    path('sports/', views.sport_list, name='sport_list'),
]
