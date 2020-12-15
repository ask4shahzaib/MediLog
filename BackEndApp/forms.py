from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

'''
class createUserForm(forms.Form):
    username = forms.CharField(
        label='CNIC', min_length=13, max_length=13, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNIC wihtout dashes'}))
    firstName = forms.CharField(
        label='firstName', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    lastName = forms.CharField(
        label='lastName', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    phone = forms.CharField(label='Phone', min_length=11, max_length=11, widget=forms.TextInput(
        attrs={'placeholder': '03XXXXXXXXX'}))
    password1 = forms.CharField(
        label='Enter Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput)

    def clean_id(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("CNIC already exists")
        return username

    def clean_phone(self):
        phone = self.cleaned_data['phone'].lower()
        r = User.objects.filter(phone=phone)
        if r.count():
            raise ValidationError("Phone already exists")
        return phone

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return self.password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['firstName'],
            self.cleaned_data['lastName'],
            self.cleaned_data['phone'],
            self.cleaned_data['password1']
        )
        return user
        '''
