from django.contrib import admin
from django.urls import path, include
from . import views  # Import the views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Home page URL
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),
    path('equipment/', include('equipment.urls')),
    path('sports/', include('sports.urls')),
    path('payments/', include('payments.urls')),
    path('my_referrals/', include('my_referrals.urls')),
]
