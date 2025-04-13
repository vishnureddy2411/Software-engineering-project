# from django.contrib import admin
# from .models import Review

# admin.site.register(Review)

from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sport', 'rating', 'created_at')  # Columns in admin list
    list_filter = ('sport', 'rating', 'created_at')  # Sidebar filters
    search_fields = ('user_username', 'sport_name', 'review_text')  # Search functionality
    readonly_fields = ('created_at',)

    # Optional: Customize the display or add actions if needed