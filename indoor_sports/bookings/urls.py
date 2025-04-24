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
    
    # Admin-related URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/bookings/', views.admin_list_bookings, name='admin_list_bookings'), # Changed
    path('admin/slots/', views.admin_list_slots, name='admin_list_slots'),     # Changed
    path('admin/slots/add/', views.admin_add_slot, name='admin_add_slot'),
    path('admin/slots/update/<int:slot_id>/', views.admin_update_slot, name='admin_update_slot'),

    path('admin/bookings/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'), # Changed
    path('admin/bookings/cancel/<int:booking_id>/', views.admin_cancel_booking, name='admin_cancel_booking'), # Changed
    path('admin/bookings/add/', views.admin_add_booking, name='admin_add_booking'), # Changed
    path('admin/bookings/update/<int:booking_id>/', views.admin_update_booking, name='admin_update_booking'), # Changed
    path('admin/bookings/delete/<int:booking_id>/', views.admin_delete_booking, name='admin_delete_booking'), # Changed
    path('admin/manage_bookings/', views.admin_manage_bookings, name='admin_manage_bookings'),
    path('admin/manage_slots/', views.admin_manage_slots, name='admin_manage_slots'),
    path('admin/slots/delete/<int:slot_id>/', views.admin_delete_slot, name='admin_delete_slot'),
    path("admin/slot_calendar/", views.admin_slot_calendar, name="admin_slot_calendar"),
    path("get_slot_data/", views.get_slot_data, name="get_slot_data"),
]


# from django.urls import path
# from . import views
# urlpatterns = [
#     # User-related URLs
#     path('choose_location/', views.choose_location, name='choose_location'),
#     path('choose_sport/<int:location_id>/', views.choose_sport, name='choose_sport'),
#     path('choose_date/<int:location_id>/<int:sport_id>/', views.choose_date, name='choose_date'),
#     path('slots/<int:location_id>/<int:sport_id>/<str:date>/', views.list_slots, name='list_slots'),
#     path('confirm_booking/<int:slot_id>/', views.confirm_booking, name='confirm_booking'),
#     path('booking_success/', views.booking_success, name='booking_success'),
#     path('my_bookings/', views.my_bookings, name='my_bookings'),
#     path('booking_detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
#     path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
#     # Admin-related URLs
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/bookings/', views.admin_list_bookings, name='admin_list_bookings'), # Changed
#     path('admin/slots/', views.admin_list_slots, name='admin_list_slots'),     # Changed
#     path('admin/slots/add/', views.admin_add_slot, name='admin_add_slot'),
#     path('admin/slots/update/<int:slot_id>/', views.admin_update_slot, name='admin_update_slot'),

#     path('admin/bookings/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'), # Changed
#     path('admin/bookings/cancel/<int:booking_id>/', views.admin_cancel_booking, name='admin_cancel_booking'), # Changed
#     path('admin/bookings/add/', views.admin_add_booking, name='admin_add_booking'), # Changed
#     path('admin/bookings/update/<int:booking_id>/', views.admin_update_booking, name='admin_update_booking'), # Changed
#     path('admin/bookings/delete/<int:booking_id>/', views.admin_delete_booking, name='admin_delete_booking'), # Changed
#     path('admin/manage_bookings/', views.admin_manage_bookings, name='admin_manage_bookings'),
#     path('admin/manage_slots/', views.admin_manage_slots, name='admin_manage_slots'),
#     path('admin/slots/delete/<int:slot_id>/', views.admin_delete_slot, name='admin_delete_slot'),
#     path("admin/slot_calendar/", views.admin_slot_calendar, name="admin_slot_calendar"),
#     path("get_slot_data/", views.get_slot_data, name="get_slot_data"),

# ]