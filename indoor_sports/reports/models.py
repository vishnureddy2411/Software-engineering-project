# from django.db import models
# from django.conf import settings

# # Import Sport and Location from your sports app
# from sports.models import Sport, Location

# class BookingReport(models.Model):
#     STATUS_CHOICES = [
#         ('Confirmed', 'Confirmed'),
#         ('Cancelled', 'Cancelled'),
#         ('Pending', 'Pending'),
#     ]
#     GENDER_CHOICES = [
#         ('Male', 'Male'),
#         ('Female', 'Female'),
#     ]

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='booking_reports'
#     )
#     sport = models.ForeignKey(
#         Sport,
#         on_delete=models.CASCADE,
#         related_name='booking_reports'
#     )
#     location = models.ForeignKey(
#         Location,
#         on_delete=models.CASCADE,
#         related_name='booking_reports'
#     )
#     date = models.DateField()
#     time = models.TimeField()
#     gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="Pending"
#     )

#     class Meta:
#         db_table = 'booking_report'

#     def __str__(self):
#         return f"{self.sport.name} at {self.location.name} on {self.date} by {self.user.username}"
