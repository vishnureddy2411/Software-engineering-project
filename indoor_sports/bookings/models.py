from django.db import models
from sports.models import Location
from accounts.models import User
from equipment.models import Equipment
from payments.models import Payment

class Slot(models.Model):
    date = models.DateField()
    time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='slots')

    def __str__(self):
        return f"{self.date} {self.time} at {self.location.name}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    equipment = models.ForeignKey(Equipment, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    slot = models.ForeignKey(Slot, null=True, blank=True, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.IntegerField(null=True, blank=True, help_text="Number of equipment items booked (if applicable)")
    booking_date = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='bookings')

    def __str__(self):
        return f"Booking {self.id} by {self.user.first_name} {self.user.last_name}"

class Confirmation(models.Model):
    CONFIRMATION_STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ]
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='confirmations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confirmations')
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, related_name='confirmations')
    rental = models.ForeignKey('equipment.Rental', null=True, blank=True, on_delete=models.SET_NULL, related_name='confirmations')
    status = models.CharField(max_length=20, choices=CONFIRMATION_STATUS_CHOICES, default='Confirmed')
    confirmation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Confirmation {self.id} - {self.status}"
