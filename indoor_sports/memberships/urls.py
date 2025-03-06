from django.urls import  path
from . import views 

urlpatterns = [
    path('memberships/', views.memberships, name='memberships'),
]