# bookings/forms.py
from django import forms
from bookings.models import Slot

class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        # List the fields that you want to display in the form.
        fields = ['date', 'time', 'slot_type', 'location', 'sport']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            # If your model later includes a price, for example:
            # 'price': forms.NumberInput(attrs={'class': 'form-control'}),
            # For other fields, you might add classes as needed.
        }
