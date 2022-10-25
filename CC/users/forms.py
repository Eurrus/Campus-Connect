from dataclasses import fields
from django import forms
from Profile.models import Profile
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200)
    password1 = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(help_text=False)
    class Meta:
        model = User
        fields = (
            'email',            
        	'username',
        )

    # email = forms.EmailField(max_length=200)
    # password1 = forms.CharField(widget=forms.PasswordInput())
    # username = forms.CharField(help_text=False)
    
    
