from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="loginpage"),  # Login page route
    path("logout/", views.logout_view, name="logout"),  # Logout route
]


