from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='USA')
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Sport(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, null=True)  # e.g., Indoor, Outdoor
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='sports')

    def __str__(self):
        return self.name

class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.IntegerField(default=20)
    image_url = models.URLField(max_length=255)

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Completed', 'Completed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    image_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

