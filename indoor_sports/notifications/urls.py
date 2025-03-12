from django.urls import path
from . import views

urlpatterns = [
    path('Notification/', views.email_list_view, name='email_list'),
    path('Notification/<int:email_id>/', views.email_detail_view, name='email_detail'),
    path('Notification/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('Notification/send/', views.send_email_to_customer_service, name='send_email_to_customer_service'),
]
