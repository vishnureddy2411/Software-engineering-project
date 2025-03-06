from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings  # For referencing AUTH_USER_MODEL

class User(models.Model):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    contact_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex='^[0-9]{10}$', message='Enter a valid 10-digit number')]
    )
    password = models.CharField(max_length=60)  # For storing hashed passwords
    address = models.TextField()
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    referral_points = models.IntegerField(default=0)
    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='referrals_made'
    )
    subscription = models.CharField(max_length=20, default='unsubscribed')
    status = models.CharField(max_length=10, default='active')
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Admin(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=60)  # For storing hashed passwords
    contact_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex='^[0-9]{10}$', message='Enter a valid 10-digit number')]
    )
    address = models.TextField()
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    created_date = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, default='active')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
