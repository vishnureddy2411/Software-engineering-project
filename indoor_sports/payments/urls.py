from django.urls import path
from . import views

urlpatterns = [
    path('user_details/', views.user_details, name='user_details'),
    path('payment_form/', views.payment_form, name='payment_form'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('success/', views.success, name='success'),
]
