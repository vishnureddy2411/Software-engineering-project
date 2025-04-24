from django.urls import path
from . import views

urlpatterns = [
    path('reviews/<int:sport_id>/', views.give_rating, name='reviews'),  
    #path('reviews/<int:location_id>/<int:sport_id>/', views.show_reviews, name='show_reviews'),
    #path('reviews/<int:booking_id>/<int:location_id>/<int:sport_id>/', views.give_rating2, name='reviews_by_location'),  
    path('reviews/<int:booking_id>/<int:location_id>/<int:sport_id>/', views.rating_based_on_location, name='reviews_by_location_booking'),
    path('reviews/<int:location_id>/<int:sport_id>/', views.rating_based_on_location, name='reviews_by_location'),
    path('admin/reviews/', views.admin_reviews, name='admin_reviews'),

]