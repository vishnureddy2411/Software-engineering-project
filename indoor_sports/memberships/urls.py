from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.membership_dashboard_view, name='membership_dashboard'),
    path('register/<str:plan_name>/', views.register_membership_view, name='register_membership'),
    path('renew/<int:membership_id>/', views.renew_membership_view, name='renew_membership'),
    path('cancel/<int:membership_id>/', views.cancel_membership_view, name='cancel_membership'),
    path('confirm-new-plan/<str:plan_name>/', views.confirm_new_plan_view, name='confirm_new_plan'),
]
