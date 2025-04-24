from django.contrib import admin
from bookings.models import BookingReport

@admin.register(BookingReport)
class BookingReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'userid', 'sport', 'location', 'date', 'time', 'gender', 'status')  # User field is valid now
    list_filter = ('sport', 'location', 'gender', 'status', 'date')
    search_fields = ('user__username', 'sport', 'location')  # No need for user__username because user is a ForeignKey now
    ordering = ('-date', '-time')
    date_hierarchy = 'date'