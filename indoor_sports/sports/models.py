from django.db import models


# -------------------------------
# Location Model
# -------------------------------
class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)  # Optional detailed address
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='USA')
    zip_code = models.CharField(max_length=20)  # Renamed from postal_code to zip_code
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sports_location'
        ordering = ['name']

    def __str__(self):
        return self.name


# -------------------------------
# Sport Model (Merged with Game)
# -------------------------------
# class Sport(models.Model):
#     sport_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100, unique=True)  # Formerly the name field in Game
#     category = models.CharField(max_length=50, null=True, blank=True)  # e.g., Indoor, Outdoor
#     # ForeignKey linking Sport to Location
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column='location_id', related_name='sports')
#     description = models.TextField(null=True, blank=True)
#     image_path = models.CharField(max_length=255, null=True, blank=True)  # Image for sport
#     price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price of the sport
#     peak_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price during peak hours
#     peak_hours_start = models.TimeField(null=True, blank=True)
#     peak_hours_end = models.TimeField(null=True, blank=True)
#     available = models.IntegerField(default=20)  # Availability of slots or resources
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'sports_sport'
#         ordering = ['name']

#     def __str__(self):
#         return self.sport_name

#     def get_current_price(self, current_time):
#         """
#         Returns the sport's price based on whether the current_time falls within peak hours.
#         """
#         if self.peak_hours_start and self.peak_hours_end:
#             if self.peak_hours_start <= current_time <= self.peak_hours_end:
#                 return self.peak_price if self.peak_price is not None else self.price
#         return self.price

from datetime import datetime, time
import pytz

class Sport(models.Model):
    sport_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # Ensure this field name is consistent
    category = models.CharField(max_length=50, null=True, blank=True)  # e.g., Indoor, Outdoor
    # ForeignKey linking Sport to Location
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column='location_id', related_name='sports')
    description = models.TextField(null=True, blank=True)
    image_path = models.CharField(max_length=255, null=True, blank=True)  # Image for sport
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price of the sport
    peak_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Price during peak hours
    peak_hours_start = models.TimeField(null=True, blank=True)
    peak_hours_end = models.TimeField(null=True, blank=True)
    available = models.IntegerField(default=20) 
  
    class Meta:
        db_table = 'sports_sport'
        ordering = ['name']

    def _str_(self):
        return self.name


    def get_current_price(self, current_time):
        """
        Returns peak price if current_time falls within peak hours, else normal price.
        Assumes peak_hours_start < peak_hours_end (same-day peak window like 19:00 to 23:00)
        """
    # Set the timezone to US timezone (e.g., New York)
        timezone = pytz.timezone('America/New_York')  # Adjust this to the specific US timezone you need
        current_time = datetime.now(timezone).time()  # Get current time in the selected timezone
    
        if self.peak_hours_start and self.peak_hours_end:
            if self.peak_hours_start <= current_time <= self.peak_hours_end:
                return self.peak_price if self.peak_price is not None else self.price
            return self.price

# -------------------------------
# Event Model
# -------------------------------
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    image_url = models.CharField(max_length=500, blank=True, null=True)  # Optional URLField
    status = models.CharField(
        max_length=20,
        choices=[('Upcoming', 'Upcoming'), ('Completed', 'Completed')],
        default='Upcoming'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sports_event'
        ordering = ['event_date']

    def __str__(self):
        return self.title


    def get_current_price(self, current_time):
        """
        Returns the game's price based on whether the current_time falls within peak hours.
        """
        if self.peak_hours_start and self.peak_hours_end:
            if self.peak_hours_start <= current_time <= self.peak_hours_end:
                return self.peak_price if self.peak_price is not None else self.price
        return self.price
