from django.urls import path
from . import views

urlpatterns = [
    path('manage-profile/', views.manage_profile, name='manage_profile'),
]