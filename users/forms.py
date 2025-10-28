from django import forms
from django.contrib.auth.models import User
from .models import  ROLE_CHOICES, DEPARTMENT_CHOICES

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES)
    contact_number = forms.CharField(max_length=15, required=False)

    def clean(self): #clean method is for cross field validation of form( specially password k liye h)
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
