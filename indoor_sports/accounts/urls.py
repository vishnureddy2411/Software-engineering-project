from django.urls import path
from .views import (
    password_reset_request,
    password_reset_confirm,
    user_dashboard_view,
    user_profile,
)
from login.views import login_view, logout_view

urlpatterns = [
    # Authentication routes
    path('login/', login_view, name='loginpage'),
    path('logout/', logout_view, name='logout'),

    path('profile/<int:user_id>/', user_profile, name='user_profile'),  # Dynamic user profile route
    path('dashboard/', user_dashboard_view, name='user_dashboard'),     # User dashboard

    # Password reset routes
    path('password-reset/', password_reset_request, name='password_reset'),                # Request password reset
    path('password-reset/<str:token>/', password_reset_confirm, name='password_reset_confirm'),  # Confirm password reset
]
