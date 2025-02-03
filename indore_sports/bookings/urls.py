from django.urls import path
from . import views

urlpatterns = [
    path('book-slot/', views.book_slot, name='book_slot'),
]