# from django.urls import path
# from . import views

# urlpatterns = [
#     path('payments/', views.payment_list, name='payment_list'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('process_payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('process_card_payment/<int:booking_id>/', views.process_card_payment, name='process_card_payment'),
    path('payments/<int:booking_id>/', views.payments_page, name='payments_page'),
    path('payment_success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
    path('error/', views.error_page, name='error_page'),
    # path("ref_cancel_booking/<int:booking_id>/", views.ref_cancel_booking, name="ref_cancel_booking"),
    # path("refunds/", views.admin_refunds, name="admin_refunds"),
    # path("approve_refund/<int:refund_id>/", views.approve_refund, name="approve_refund"),
    # path("reject_refund/<int:refund_id>/", views.reject_refund, name="reject_refund"),

    path('admin/payments/', views.admin_view_payments, name='admin_view_payments'),
    path('admin/payments/refund/<int:id>/', views.process_refund, name='process_refund'),  # Use `id` here   


]
