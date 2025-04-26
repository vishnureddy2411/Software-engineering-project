from django.urls import path
from . import views
 
urlpatterns = [
    
    path('reviews/<int:booking_id>/<int:location_id>/<int:sport_id>/', views.rating_based_on_location, name='reviews_by_location_booking'),
    path('reviews/<int:location_id>/<int:sport_id>/', views.rating_based_on_location, name='reviews_by_location'),
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),
    path('give_rating/<int:sport_id>/<int:location_id>/', views.give_rating, name='give_rating'),
 
]
 