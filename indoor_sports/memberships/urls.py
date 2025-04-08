from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.membership_dashboard_view, name='membership_dashboard'),
    path('register/<str:plan_name>/', views.register_membership_view, name='register_membership'),
    path('renew/<int:membership_id>/', views.renew_membership_view, name='renew_membership'),
    path('cancel/<int:membership_id>/', views.cancel_membership_view, name='cancel_membership'),
    path('confirm-new-plan/<str:plan_name>/', views.confirm_new_plan_view, name='confirm_new_plan'),
    path('admin-dashboard/view-memberships/', views.view_user_memberships, name='view_user_memberships'),
    path('membership_plans/', views.membership_plan_list, name='membership_plan_list'),

    # URL for updating a specific membership plan
    path('membership_plans/update/<int:plan_id>/', views.update_membership_plan, name='update_membership_plan'),

    # URL for deleting a specific membership plan
    path('membership_plans/delete/<int:plan_id>/', views.delete_membership_plan, name='delete_membership_plan'),
    
    path('create-checkout-session/<str:plan>/', views.create_checkout_session, name='create_checkout_session'),
    path('subscription_payment_success/<str:plan>/', views.subscription_payment_success, name='subscription_payment_success'),
    path('subscription_payment_cancel/', views.subscription_payment_cancel, name='subscription_payment_cancel'),
]