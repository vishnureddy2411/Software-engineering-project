import datetime
from django.db import models
from django.conf import settings
from equipment.models import Equipment
from payments.models import Payment
from django.core.validators import MinValueValidator

# ------------------------------------------------------------------------------
# Slot Model: Represents available time slots at a location for a specific sport.
# ------------------------------------------------------------------------------
class Slot(models.Model):
    slot_id = models.BigAutoField(primary_key=True)
    SLOT_TYPE_CHOICES = [
        ('Peak', 'Peak Hours'),
        ('Non-Peak', 'Non-Peak Hours'),
    ]
    date = models.DateField()
    time = models.TimeField()
    slot_type = models.CharField(
        max_length=20,
        choices=SLOT_TYPE_CHOICES,
        default='Non-Peak'
    )
    is_booked = models.BooleanField(default=False)
    location = models.ForeignKey("sports.Location", on_delete=models.CASCADE, related_name="slots")
    sport = models.ForeignKey("sports.Sport", on_delete=models.CASCADE, related_name="slots")
    is_active = models.BooleanField(default=True)  # Add this field


    def __str__(self):
        return f"{self.date} {self.time} ({self.slot_type}) at {self.location.name}"

    def get_price(self):
        """
        Returns the slot price based on its type.
        If the slot is during peak hours and the sport defines a peak_price, that price is used;
        otherwise, the standard price is returned.
        """
        if self.slot_type == "Peak":
            return self.sport.peak_price if self.sport.peak_price is not None else self.sport.price
        return self.sport.price




# ------------------------------------------------------------------------------
# Booking Model: Represents a user's booking for a sport at a specific slot.
# ------------------------------------------------------------------------------
class Booking(models.Model):
    booking_id = models.BigAutoField(primary_key=True)
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    sport = models.ForeignKey("sports.Sport", on_delete=models.CASCADE, related_name="bookings")
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="bookings") 
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Booked"
    )
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Number of equipment items booked (if applicable)"
    )
    equipment = models.ForeignKey(
        Equipment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bookings"
    )
    date = models.DateField(default=datetime.date.today) 
    time_slot = models.TimeField(null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey("sports.Location", on_delete=models.CASCADE, related_name="bookings")
    submitted_review = models.BooleanField(default=False)
    def __str__(self):
        full_name = getattr(self.user, "get_full_name", lambda: self.user.username)()
        return f"Booking {self.id} by {full_name} for {self.sport.name}"
    
    class Meta:
        db_table = 'bookings_booking'
        ordering = ['sport']




# ------------------------------------------------------------------------------
# BookingReport Model: Used to generate booking reports.
# ------------------------------------------------------------------------------
class BookingReport(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending'),
    ]
    SPORT_CHOICES = [
        ('Cricket', 'Cricket'),
        ('Football', 'Football'),
        ('Tennis', 'Tennis'),
        ('Basketball', 'Basketball'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    userid = models.IntegerField()
    sport = models.CharField(max_length=100, choices=SPORT_CHOICES)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES, 
        default="Pending"
    )

    class Meta:
        db_table = 'booking_report'

    def __str__(self):
        return f"{self.sport} at {self.location} on {self.date} by user {self.userid}"




# ------------------------------------------------------------------------------
# Confirmation Model: Links payments, bookings, and optionally rentals to confirmation statuses.
# ------------------------------------------------------------------------------
class Confirmation(models.Model):
    CONFIRMATION_STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ]
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="confirmations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="confirmations")
    booking = models.ForeignKey(
        Booking, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmations"
    )
    rental = models.ForeignKey(
        "equipment.Rental", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmations"
    )
    status = models.CharField(
        max_length=20,
        choices=CONFIRMATION_STATUS_CHOICES,
        default="Confirmed"
    )
    confirmation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Confirmation {self.id} - {self.status}"
