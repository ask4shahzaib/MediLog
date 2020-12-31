from django.core.exceptions import ObjectDoesNotExist
from BackEndApp.models import Patient
from django.contrib import auth
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, password_validation
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import *
from django.contrib.auth.models import Group


@login_required(login_url='login')
def home(request):
    return render(request, 'BackEndApp/patient_home.html')


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Doctor', 'Hospital'])
def feed(request):
    patient = Patient.objects.get(CNIC=request.session['id'])
    context = {'patient': patient}
    return render(request, 'BackEndApp/patient_home.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session['id'] = username
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
    if request.method == 'POST':
        cnic = request.POST['cnic']
        password = request.POST['password']
        fname = request.POST['fname']
        lname = request.POST['lname']
        phone = request.POST['phone']
        email = request.POST['email']
        age = request.POST['age']
        age = int(age)
        address = request.POST['address']
        photo = request.FILES['photo']
        try:
            y = User.objects.get(username=cnic)
        except ObjectDoesNotExist:
            y = None
        if y is None:
            x = User.objects.create_user(
                username=cnic, first_name=fname, last_name=lname, password=password, email=email)
            x.save()
            group = Group.objects.get(name='Patient')
            x.groups.add(group)
            z = Patient(CNIC=cnic, fName=fname, lName=lname,
                        age=age, phone=phone, address=address, email=email, photo=photo, user=x, verification=False)
            z.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('login')
        else:
            messages.error(
                request, "Already a patient found with same CNIC")
            return redirect('register')
    else:
        return render(request, 'BackEndApp/register.html')
