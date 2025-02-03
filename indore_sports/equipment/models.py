from django.db import models

class Equipment(models.Model):
    sport = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    price = models.FloatField()