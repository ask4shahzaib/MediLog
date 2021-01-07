from datetime import timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import json
from BackEndApp.models import Patient, Doctor, Laboratory, Hospital, Prescription, prescriptions
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import *
import datetime
from django.contrib.auth.models import Group, User


@login_required(login_url='login')
def viewPrescription(request):
    group = request.user.groups.all()
    group = str(group[0])
    check = False

    if group == 'Patient':
        check = True
    person = Patient.objects.filter(CNIC=request.user.username)
    person = person[0]
    prescriptions = ""
    try:
        prescriptions = Prescription.objects.filter(patient=person.CNIC)
    except:
        prescriptions = None
    if prescriptions is not None:
        for prescription in prescriptions:
            prescription.doctor = doctorName(prescription.doctor)
            prescription.hospital = hospitalName(prescription.hospital)

    context = {'prescriptions': prescriptions}
    return render(request, "BackEndApp/prescriptions.html", context)


@login_required(login_url='login')
def summary(request):
    group = request.user.groups.all()
    group = str(group[0])
    check = False

    if group == 'Patient':
        check = True

    if check == True:
        patient = Patient.objects.filter(CNIC=request.user.username)
        patient = patient[0]
        context = {'patient': patient, 'check': check}
        return render(request, "BackEndApp/summary.html", context)

    if request.method == 'POST':
        id = request.POST['cnic']
        patient = ""
        try:
            patient = Patient.objects.filter(CNIC=id)
            patient = patient[0]
        except:
            messages.error(request, "Patient not found")
            return redirect('feed')
        context = {'patient': patient, 'check': check}
        return render(request, "BackEndApp/summary.html", context)
    else:
        return redirect('feed')


@login_required(login_url='login')
def profile(request):
    group = request.user.groups.all()
    group = str(group[0])
    id = request.user.username
    person = ""
    patient = False
    if group == 'Patient':
        patient = True
        person = Patient.objects.filter(CNIC=id)
        person = person[0]

    if group == 'Doctor':
        person = Doctor.objects.filter(license_No=id)
        person = person[0]

    if request.method == 'GET':
        context = {'person': person, 'patient': patient}
        return render(request, "BackEndApp/Profile.html", context)

    elif request.method == 'POST':
        form = PatientProfileForm(request.POST)
        if form.is_valid():
            form .save()
        person = Patient.objects.filter(CNIC=id)
        person = person[0]
        context = {'person': person, 'patient': patient}
        return render(request, "BackEndApp/Profile.html", context)


@login_required(login_url='login')
def home(request):
    return redirect('login')


def doctorName(license):
    try:
        doctor = Doctor.objects.filter(license_No=license)
        doctor = doctor[0]
        doctor = doctor.fName+" "+doctor.lName
        if len(doctor) > 19:
            doctor = doctor[0:19]
            doctor = doctor+' ...'
    except:
        doctor = "N/A"
    return doctor


def hospitalName(id):
    try:
        hospital = Hospital.objects.filter(id=id)
        hospital = hospital[0]
        hospital = hospital.name
        if len(hospital) > 18:
            hospital = hospital[0:18]
            hospital = hospital+'...'
    except:
        hospital = "N/A"
    return hospital


def graphData(prescriptions):
    start_date = datetime.datetime.today()
    start_date = str(start_date).split(' ')[0]
    start_date = str(start_date)
    start_date = datetime.datetime.strptime(
        start_date, '%Y-%m-%d').date()
    delta = timedelta(days=1)
    visits = 0
    visitcount = []
    for i in range(7):
        for prescription in prescriptions.iterator():
            if(prescription.date == start_date):
                visits += 1
        start = str(start_date)
        temp = datetime.datetime.strptime(
            start, '%Y-%m-%d').strftime("%d/%m/%Y")
        visitcount.append([str(temp), visits, 0])
        start_date -= delta

    def first(obj):
        return obj[0]
    visitcount.sort(key=first)
    visitcount = [['Date', 'Visits to Doctor', 'Tests']] + visitcount
    return visitcount


@login_required(login_url='login')
def patientFeed(request, id):
    patient = Patient.objects.get(CNIC=id)
    try:
        prescriptions = Prescription.objects.filter(
            patient=request.user.username).order_by('-date')

        visitcount = graphData(prescriptions)

        license = prescriptions[0].doctor
        doctor = doctorName(license)

        hospital = prescriptions[0].hospital
        hospital = hospitalName(hospital)

        date = prescriptions[0].date

        prescriptions = prescriptions[0:3]
        for prescription in prescriptions:
            prescription.doctor = doctorName(prescription.doctor)

    except:
        visitcount = [['Date', 'Visits to Doctor',
                       'Tests'], ['2020', 0, 0], ['2019', 0, 0]]
        doctor = 'N/A'
        date = 'N/A'
        hospital = hospitalName(doctor)
        prescriptions = None

    context = {'patient': patient,
               'prescriptions': prescriptions, 'doctor': doctor, 'hospital': hospital, 'date': date, 'vis': json.dumps(visitcount)}

    return render(request, 'BackEndApp/patientHomePage.html', context)


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Laboratory', 'Management', 'Doctor', 'Hospital'])
def feed(request):
    group = request.user.groups.all()
    group = str(group[0])
    id = request.user.username
    if (group == 'Patient'):
        return patientFeed(request, id)

    if (group == 'Laboratory'):
        lab = Laboratory.objects.get(id=id)
        context = {'lab': lab}
        return render(request, 'BackEndApp/lab_home.html', context)

    if (group == 'Doctor'):
        doctor = Doctor.objects.get(license_No=id)
        context = {'doctor': doctor}
        return render(request, 'BackEndApp/doctorHomePage.html', context)

    if (group == 'Hospital'):
        hospital = Hospital.objects.get(id=id)
        context = {'hospital': hospital}
        return render(request, 'BackEndApp/hospitalHomePage.html', context)

    if (group == 'Management'):
        context = {'user': request.user}
        return render(request, 'BackEndApp/management_home.html', context)


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


@allowed_users(allowed=['Hospital'])
def addPrescription(request):
    if request.method == "POST" and request.FILES['file']:
        file = request.FILES['file']
        patient = request.POST.get('patient')
        try:
            Patient.objects.get(CNIC=patient)
        except:
            messages.error(request, "Incorrect Patient CNIC")
            return redirect('addPrescription')
        doctor = request.POST.get('doctor')
        label = request.POST.get('label')
        try:
            Doctor.objects.get(license_No=doctor)
        except:
            messages.error(request, "Incorrect Doctor License Number")
            return redirect('addPrescription')
        hospital = request.user.username
        description = request.POST.get('description')
        date = request.POST.get('date')
        date = datetime.datetime.strptime(
            date, '%Y-%m-%d').strftime("%Y-%m-%d")
        x = Prescription(file=file, date=date, description=description,
                         patient=patient, label=label, doctor=doctor, hospital=hospital)
        x.save()
    hospital = Hospital.objects.get(id=request.user.username)
    context = {'hospital': hospital}
    return render(request, 'BackEndApp/hospitalHomePage.html', context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def register(request):
    if request.method == 'POST':
        group = request.user.groups.all()
        try:
            group = str(group[0])
        except:
            group = 'Patient'
        if group == 'Patient':
            verification = False
        else:
            verification = True
        cnic = request.POST['cnic']
        password = request.POST['password']
        fname = request.POST['fname']
        lname = request.POST['lname']
        phone = request.POST['phone']
        email = request.POST['email']
        dob = request.POST['dob']
        address = request.POST['address']
        try:
            photo = request.FILES['photo']
        except:
            photo = None
        try:
            y = User.objects.get(username=cnic)
        except ObjectDoesNotExist:
            y = None
        if y is None:
            x = User.objects.create_user(
                username=cnic, first_name=fname, last_name=lname, password=password, email=email)
            x.save()
            try:
                group = Group.objects.get(name='Patient')
            except:
                group = Group(name='Patient')
                group.save()
                group = Group.objects.get(name='Patient')
            x.groups.add(group)
            if photo != None:
                z = Patient(CNIC=cnic, fName=fname, lName=lname,
                            dob=dob, phone=phone, address=address, email=email, photo=photo, user=x, verification=verification)
                z.save()
            else:
                z = Patient(CNIC=cnic, fName=fname, lName=lname,
                            dob=dob, phone=phone, address=address, email=email, user=x, verification=verification)
                z.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('login')
        else:
            messages.error(
                request, "Already a patient found with same CNIC")
            return redirect('register')
    else:
        return render(request, 'BackEndApp/register.html')
