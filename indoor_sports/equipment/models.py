from django.db import models
from accounts.models import User
from sports.models import Location

class Equipment(models.Model):
    equipment_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    quantity = models.IntegerField()
    condition_of_kit = models.CharField(max_length=20, default='Good')  # e.g., New, Good, Needs Repair
    availability_status = models.CharField(max_length=20, default='Available')
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Added price column
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  # Ensure you have this relationship



    def _str_(self):
        return self.name

class Rental(models.Model):
    RENTAL_STATUS_CHOICES = [
        ('Rented', 'Rented'),
        ('Returned', 'Returned'),
        ('Late', 'Late'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='rentals')
    quantity = models.IntegerField()
    rental_start = models.DateTimeField()
    rental_end = models.DateTimeField(null=True, blank=True)
    rental_status = models.CharField(max_length=20, choices=RENTAL_STATUS_CHOICES, default='Rented')
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Rental {self.id} - {self.equipment.name}"