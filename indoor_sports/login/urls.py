from django.urls import  path
from . import views 

urlpatterns = [
    path('loginpage/', views.loginpage, name='loginpage'),
]