from django.db import models
from accounts.models import User

class Referral(models.Model):
    referrer_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='referrals_given'
    )
    referred_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='referrals_received',
        null=True, 
        blank=True
    )
    friend_email = models.EmailField(
        null=True, 
        blank=True, 
        help_text="Email address of the friend being referred"
    )
    points_earned = models.IntegerField(default=0)
    redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.redeemed:
            return f"Referral from {self.referrer_user.username} to {self.referred_user.username}"
        else:
            return f"Pending referral from {self.referrer_user.username} to {self.friend_email or 'N/A'}"
