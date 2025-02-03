from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sport = models.CharField(max_length=100)
    date = models.DateField()
    time_slot = models.TimeField()
    status = models.CharField(max_length=50, default='booked')