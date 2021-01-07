from BackEndApp.models import Patient
from django import forms
from django.forms.widgets import EmailInput, PasswordInput
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.core.exceptions import ValidationError


class PatientProfileForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['fName', 'lName', 'phone', 'address', 'email']
