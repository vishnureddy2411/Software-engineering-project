
# from django import forms
# from bookings.models import Slot

# class SlotForm(forms.ModelForm):
#     class Meta:
#         model = Slot
#         # List the fields that you want to display in the form.
#         fields = ['date', 'time', 'slot_type', 'location', 'sport']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
#             # If your model later includes a price, for example:
#             # 'price': forms.NumberInput(attrs={'class': 'form-control'}),
#             # For other fields, you might add classes as needed.
#         }


from django import forms
from bookings.models import Slot, Booking
from equipment.models import Equipment
from django.contrib.auth import get_user_model

User = get_user_model()

class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ['date', 'time', 'slot_type', 'location', 'sport', 'is_booked']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class BookingAdminUpdateForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="User", required=False)
    slot = forms.ModelChoiceField(queryset=Slot.objects.all(), label="Slot", required=False)
    class Meta:
        model = Booking
        fields = ['user', 'slot', 'status', 'quantity', 'equipment', 'date', 'time_slot'] # Added 'equipment'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance'):
            instance = kwargs.get('instance')
            self.fields['user'].initial = instance.user
            self.fields['slot'].initial = instance.slot
            self.fields['date'].initial = instance.date
            self.fields['time_slot'].initial = instance.time_slot

class BookingAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="User")
    slot = forms.ModelChoiceField(queryset=Slot.objects.filter(is_booked=False), label="Available Slot")
    quantity = forms.IntegerField(min_value=1, initial=1, help_text="Number of participants/items",
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    equipment = forms.ModelChoiceField(queryset=Equipment.objects.all(), label="Equipment (if applicable)",
                                         required=False) # Added equipment field
    status = forms.ChoiceField(choices=Booking.STATUS_CHOICES, initial='Booked',
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Booking
        fields = ['user', 'slot', 'quantity', 'equipment', 'status'] # Added 'equipment'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slot'].label_from_instance = self.slot_label_from_instance

    def slot_label_from_instance(self, obj):
        return f"{obj.date} {obj.time.strftime('%H:%M')} ({obj.slot_type}) at {obj.location.name} - Sport: {obj.sport.name}"

    def save(self, commit=True):
        booking = super().save(commit=False)
        selected_slot = self.cleaned_data['slot']
        booking.location = selected_slot.location
        booking.sport = selected_slot.sport
        booking.date = selected_slot.date
        booking.time_slot = selected_slot.time
        if commit:
            booking.save()
            selected_slot.is_booked = True
            selected_slot.save()
        return booking
