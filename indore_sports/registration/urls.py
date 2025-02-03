from django.urls import  path
from . import views 

urlpatterns = [
    path('registerpage/', views.registerpage, name='registerpage'),
]