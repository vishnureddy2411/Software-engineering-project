from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.register_user, name="register_user"),
    path('invite_user/', views.invite_user, name="invite_user"),
    path('register_new_user/', views.register_new_user, name="register_new_user"),
    path('add_admin/', views.add_admin, name="add_admin"),
    path('register_admin/', views.register_new_admin, name="register_new_admin"),
    path('check_email_exists/', views.check_email_exists, name='check_email_exists'),
    path('check_username/', views.check_username, name="check_username"),
    path('get-location/', views.get_location_from_zipcode, name='get_location'),
]



