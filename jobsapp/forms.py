from django import forms

from .models import Jobquery

class ContactForm(forms.Form):
    sender = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

        
