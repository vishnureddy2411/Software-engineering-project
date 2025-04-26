from django import forms
from sports.models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'location', 'image_url', 'status']
        widgets = {
            'event_date': forms.TextInput(attrs={'id': 'id_event_date'}),
        }



