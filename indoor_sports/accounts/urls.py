from django.urls import path
from .views import (
    password_reset_request,
    password_reset_confirm,
    manage_profile,
)
from login.views import login_view, logout_view

urlpatterns = [
    path('login/', login_view, name='loginpage'),
    path('logout/', logout_view, name='logout'),
    path('manage-profile/', manage_profile, name='manage_profile'),
    path("password-reset/", password_reset_request, name="password_reset"),
    path("password-reset/<str:token>/", password_reset_confirm, name="password_reset_confirm"),
]
