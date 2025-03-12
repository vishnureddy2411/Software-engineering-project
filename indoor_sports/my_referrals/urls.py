from django.urls import path
from . import views

urlpatterns = [
    path("my_referrals/", views.my_referrals, name="my_referrals"),
]
