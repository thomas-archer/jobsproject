from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)        
        for fieldname in ['username', 'password1']:
            self.fields[fieldname].help_text = None
        self.fields['password1'].help_text = "Your password must contain at least 8 characters."

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username','email']

        help_texts = {
            'username': ('Only used when logging in to our site.'),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name','phone','org','linkedin_URL','resume','github_URL','twitter_URL','portfolio_URL','comments']
        labels = {
            'name': ('Full Name*'),
            'phone': ('Phone*'),
            'org': ('Current Company*'),
            'resume': ('Resume* (Max File Size: 1MB)'),
            'comments': ('Additional information (anything else you would like employers to know)'),
            'linkedin_URL': ('Linkedin URL*')
        }
        help_texts = {
            'org': (''),
        }

