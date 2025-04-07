from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.membership_dashboard_view, name='membership_dashboard'),
    path('register/<str:plan>/', views.register_membership_view, name='register_membership'),
    path('renew/<int:id>/', views.renew_membership_view, name='renew_membership_view'),
    path('cancel/<int:id>/', views.cancel_membership_view, name='cancel_membership'),
    path('confirm-new-plan/<str:plan>/', views.confirm_new_plan_view, name='confirm_new_plan'),
    path('create-checkout-session/<str:plan>/', views.create_checkout_session, name='create_checkout_session'),
    path('subscription_payment_success/<str:plan>/', views.subscription_payment_success, name='subscription_payment_success'),
    path('subscription_payment_cancel/', views.subscription_payment_cancel, name='subscription_payment_cancel'),
]
