from django import forms
from django.forms.widgets import EmailInput, PasswordInput
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.core.exceptions import ValidationError


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=100, label='Phone')

    class Meta:
        model = User
        fields = ["username", "email", "phone",
                  "password1", "password2"]
