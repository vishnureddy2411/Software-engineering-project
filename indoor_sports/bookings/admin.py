# from django.contrib import admin
# from .models import Booking

# admin.site.register(Booking)



from django.contrib import admin,messages
from .models import Slot, Booking, BookingReport, Confirmation
from .forms import BookingAdminForm ,BookingAdminUpdateForm

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('slot_id', 'date', 'time', 'slot_type', 'is_booked', 'location', 'sport')
    list_filter = ('location', 'sport', 'slot_type', 'is_booked', 'date')
    search_fields = ('location__name', 'sport__name')
    date_hierarchy = 'date'
    ordering = ('slot_id', 'date', 'time')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = ('booking_id', 'user', 'slot', 'status', 'booking_date','equipment') #added equipment to list_display
    list_filter = ('status', 'slot__sport', 'booking_date', 'slot__date', 'slot__location')
    search_fields = ('user__username', 'slot__sport__name', 'booking_id')
    date_hierarchy = 'booking_date'
    ordering = ('-booking_date',)
    readonly_fields = ('booking_date',)
    # Removed location, sport, date, time, available_slots from fieldsets
    fieldsets = (
        (None, {
            'fields': ('user', 'slot', 'quantity', 'equipment', 'status') # Added 'equipment'
        }),
        ('Booking Details', {
            'fields': ('booking_date',),
            'classes': ('collapse',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Override to use different forms for adding and updating.
        """
        if obj:  # This is an update.
            return BookingAdminUpdateForm
        else:  # This is a new booking.
            return BookingAdminForm

    def save_model(self, request, obj, form, change):
        # Ensure the selected slot is marked as booked
        if not change:
            selected_slot = form.cleaned_data['slot']
            if selected_slot and not selected_slot.is_booked:
                selected_slot.is_booked = True
                selected_slot.save()
                obj.location = selected_slot.location
                obj.sport = selected_slot.sport
                obj.date = selected_slot.date
                obj.time_slot = selected_slot.time
            elif selected_slot and selected_slot.is_booked:
                messages.error(request, f"The selected slot (ID: {selected_slot.slot_id}) is already booked.")
                return None  # Prevent saving the booking
            elif not selected_slot:
                messages.error(request, "Please select an available slot.")
                return None

        super().save_model(request, obj, form, change)
        if change:
            print(f"Booking {obj.booking_id} updated by admin.")

    def delete_model(self, request, obj):
        # Free up the slot when a booking is deleted
        if obj.slot:
            obj.slot.is_booked = False
            obj.slot.save()

        super().delete_model(request, obj)

# @admin.register(BookingReport)
# class BookingReportAdmin(admin.ModelAdmin):
#     list_display = ('id', 'userid', 'sport', 'location', 'date', 'time', 'gender', 'status')
#     list_filter = ('sport', 'location', 'date', 'status', 'gender')
#     search_fields = ('location', 'sport', 'userid')
#     date_hierarchy = 'date'
#     ordering = ('-date', '-time')
#     readonly_fields = ('userid', 'sport', 'location', 'date', 'time', 'gender', 'status')
#     fieldsets = (
#         (None, {
#             'fields': ('userid', 'sport', 'location', 'date', 'time', 'gender', 'status')
#         }),
#     )

@admin.register(Confirmation)
class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'user', 'booking', 'rental', 'status', 'confirmation_date')
    list_filter = ('status', 'confirmation_date')
    search_fields = ('user__username', 'booking__booking_id', 'rental__id')
    date_hierarchy = 'confirmation_date'
    ordering = ('-confirmation_date',)
    readonly_fields = ('confirmation_date',)
    fieldsets = (
        (None, {
            'fields': ('payment', 'user', 'booking', 'rental', 'status')
        }),
        ('Confirmation Details', {
            'fields': ('confirmation_date',),
            'classes': ('collapse',),
        }),
    )