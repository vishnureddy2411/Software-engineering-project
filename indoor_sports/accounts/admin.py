from django.contrib import admin
from .models import User, Profile, Admin

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'emailid', 'firstname', 'lastname', 'status')
    search_fields = ('username', 'emailid')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
