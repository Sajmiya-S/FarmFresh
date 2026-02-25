from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['email','phone']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['customer']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your email address'}),
            'phone': forms.NumberInput(attrs={'placeholder': 'Your phone number'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Type your message here...',
                'rows': 5, 
                'cols': 40
            })
        }
