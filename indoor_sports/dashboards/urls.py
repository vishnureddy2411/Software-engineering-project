# from django.urls import path
# from dashboards import views

# urlpatterns = [
#     path('user/', views.user_dashboard, name='user_dashboard'),  # User Dashboard
#     path('admin/', views.admin_dashboard, name='admin_dashboard'),  # Admin Dashboard
#     path('admin/card_01/', views.admin_card_01, name='admin_card_01'),
# ]

from django.urls import path
from .views import (
    admin_dashboard, user_dashboard, home, edit_profile, view_sports, add_sport,
    del_sport, update_sport, view_bookings, view_payments, contact,admin_card_01,view_users,admin_card_03,add_users,add_admins
)

urlpatterns = [
    path('', home, name='home'),
    path('user_dashboard/', user_dashboard, name="user_dashboard"),
    path('admin_dashboard/', admin_dashboard, name="admin_dashboard"),
    path('admin_card_01/', admin_card_01, name="admin_card_01"),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('view_sports/', view_sports, name='view_sports'),
    path('add_sport/', add_sport, name='add_sport'),
    path('del_sport/', del_sport, name='del_sport'),
    path('update_sport/', update_sport, name='update_sport'),
    path('view_bookings/', view_bookings, name='view_bookings'),
    path('view_users/', view_users, name='view_users'),
    path('admin_card_03/', admin_card_03, name='admin_card_03'),
    path('view_payments/', view_payments, name='view_payments'),
    path('add_users/', add_users, name='add_users'),
    path('add_admin/', add_admins, name='add_admins'),
    path('contact/', contact, name='contact'),
]
