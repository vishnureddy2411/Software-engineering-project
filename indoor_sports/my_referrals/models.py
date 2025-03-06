from django.db import models
from accounts.models import User

class Referral(models.Model):
    referrer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_given')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')
    points_earned = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Referral from {self.referrer_user.username} to {self.referred_user.username}"
