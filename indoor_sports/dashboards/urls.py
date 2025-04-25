

from django.urls import path

from .views import (
    admin_dashboard, user_dashboard, home, edit_profile, view_sports, add_sport,
    del_sport, update_sport, view_bookings, view_payments, contact,admin_card_01,view_users,admin_card_03,add_users,add_admins,add_slot,list_events,create_event,update_event,delete_event,privacy_policy,Terms_service,about_us,edit_profile_admin
) 

urlpatterns = [
    path('', home, name='home'),
    path('user_dashboard/', user_dashboard, name="user_dashboard"),
    path('admin_dashboard/', admin_dashboard, name="admin_dashboard"),
    path('admin_card_01/', admin_card_01, name="admin_card_01"),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('view_sports/', view_sports, name='view_sports'),
    path('add_sport/', add_sport, name='add_sport'),
    path('update_sport/<int:sport_id>/', update_sport, name='update_sport'),
    path('del_sport/<int:sport_id>/', del_sport, name='del_sport'),
    path('view_bookings/', view_bookings, name='view_bookings'),
    path('view_users/', view_users, name='view_users'),
    path('admin_card_03/', admin_card_03, name='admin_card_03'),
    path('view_payments/', view_payments, name='view_payments'),
    path('add_users/', add_users, name='add_users'),
    path('add_admin/', add_admins, name='add_admins'),
    path('contact/', contact, name='contact'),
    path('add-slot/', add_slot, name='add-slot'),
    path('list_events',list_events,name='list_events'),
    path('create_event',create_event,name='create_event'),
    path('update_event/<int:event_id>/', update_event, name='update_event'),
    path('delete_event/<int:event_id>/', delete_event, name='delete_event'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('Terms_service/', Terms_service, name='Terms_service'),
    path('about-us/', about_us, name='about_us'),
    path('edit_profile_admin/',edit_profile_admin, name='edit_profile_admin'),
     
]

