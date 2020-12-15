from django.contrib import auth
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, password_validation
from django.shortcuts import render, redirect
from .forms import CreateUserForm, RegisterForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def home(request):
    return HttpResponse("Hello, Django!")


@login_required(login_url='login')
def feed(request):
    return HttpResponse('Hello User you are in 😉')


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('feed')
    else:
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


def register(request):
    if request.user.is_authenticated:
        return redirect('feed')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Account Created Succesfully')
                return redirect('loginPage')
        context = {'form': form}
        return render(request, 'BackEndApp/register.html', context)
