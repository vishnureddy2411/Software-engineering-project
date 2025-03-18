from django.urls import path
from . import views
urlpatterns = [
    path("choose-location/", views.choose_location, name="choose_location"),
    path("choose-sport/<int:location_id>/", views.choose_sport, name="choose_sport"),
    path("choose-date/<int:location_id>/<int:sport_id>/", views.choose_date, name="choose_date"),
    path("slots/<int:location_id>/<int:sport_id>/<date>/", views.list_slots, name="list_slots"),
    path("confirm/<int:slot_id>/", views.confirm_booking, name="confirm_booking"),
    path("booking-success/", views.booking_success, name="booking_success"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("admin/add-slot/", views.add_slot, name="add_slot"),
]
