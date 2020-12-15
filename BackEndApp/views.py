from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
#from .forms import createUserForm
from django.contrib.auth.forms import UserCreationForm


def home(request):
    return HttpResponse("Hello, Django!")


def name(request, name):
    return HttpResponse("My name is Shah Zaib Ali Dogar and my partners name is "+name)


def login(request):
    context = {}
    return render(request, 'BackEndApp/login.html', context)


def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'BackEndApp/register.html', context)
