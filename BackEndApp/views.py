from BackEndApp.models import Patient
from django.contrib import auth
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, password_validation
from django.shortcuts import render, redirect
from .forms import CreateUserForm, RegisterForm
from django.contrib.auth.decorators import login_required
from .decorators import *
from django.contrib.auth.models import Group


@login_required(login_url='login')
def home(request):
    return HttpResponse("Hello, Home Page!")


@login_required(login_url='login')
def feed(request):
    return HttpResponse('Hello Patient you are in 😉')


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'BackEndApp/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Patient')
            messages.success(request, 'Account Created Succesfully')
            user.groups.add(group)
            Patient.objects.create(
                user=user
            )
            return redirect('login')
    context = {'form': form}
    return render(request, 'BackEndApp/register.html', context)
