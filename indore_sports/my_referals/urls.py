from django.urls import  path
from . import views 

urlpatterns = [
    path('myreferals/', views.myreferals, name='myreferals'),
]