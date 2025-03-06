from django.db import models
from django.contrib.auth.models import User
from sports.models import Sport  # Import Sport model from sports app

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()  # You might add validators for 1–5 range
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} for {self.sport.name}"