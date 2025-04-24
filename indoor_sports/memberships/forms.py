from django import forms
from .models import Membership, MembershipPlan

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['plan', 'price', 'status']  # Include only the fields you want to update
        widgets = {
            'plan': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=[('active', 'Active'), ('inactive', 'Inactive')], attrs={'class': 'form-control'}),
        }


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'price', 'duration', 'description']