from django.db import models
from django.conf import settings  # Import settings to reference AUTH_USER_MODEL

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom User model
        on_delete=models.CASCADE
    )
    sport = models.ForeignKey('sports.Sport', on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField()
    location = models.ForeignKey("sports.Location", on_delete=models.CASCADE, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for sport {self.sport.name}"

