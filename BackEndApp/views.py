import os
from calendar import month_name
from datetime import timedelta
from time import strptime
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import json
from BackEndApp.models import LabReport, Patient, Doctor, Laboratory, Hospital, Prescription, prescriptions, reports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import *
import datetime
from django.contrib.auth.models import Group, User


def timeline(request):
    if request.method == 'POST':
        date = request.POST['q']
        date = date.split(' ')
        month = date[0]
        month = strptime(month, '%B').tm_mon
        if month < 10:
            month = '0' + str(month)
        start = [date[1] + "-" + str(month) + "-" + '01']
        end = [date[1] + "-" + str(month) + "-" + '31']
        request.session['start'] = start
        request.session['end'] = end
        return viewAllRecords(request)

    data = timelineData(request.user.username)
    context = {
        'data': data
    }
    return render(request, "BackEndApp/timeLine.html", context)


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Doctor'])
def viewAllRecords(request):
    group = request.user.groups.all()
    group = str(group[0])
    check = False
    doctor = ""

    if group == 'Patient':
        check = True
        person = Patient.objects.filter(CNIC=request.user.username)
        person = person[0]
    else:
        try:
            cnic = request.POST['cnic']
            person = Patient.objects.filter(CNIC=cnic)
            person = person[0]
        except:
            return redirect('feed')
        doctor = Doctor.objects.filter(license_No=request.user.username)
        doctor = doctor[0]

    prescriptions = ""
    try:
        if request.session.has_key('start') and request.session.has_key('end'):
            prescriptions = Prescription.objects.filter(patient=person.CNIC)
            print(prescriptions[0])
            prescriptions = prescriptions.filter(
                date__range=[request.session['start'][0], request.session['end'][0]])
            print(prescriptions[0])
        else:
            prescriptions = Prescription.objects.filter(patient=person.CNIC)
    except:
        prescriptions = None
    try:
        if request.session.has_key('start') and request.session.has_key('end'):
            reports = LabReport.objects.filter(patient=person.CNIC)
            print(reports[0])
            reports = reports.filter(
                date__range=[request.session['start'][0], request.session['end'][0]])
            print(reports[0])
        else:
            reports = LabReport.objects.filter(patient=person.CNIC)
    except:
        reports = None
    if prescriptions is not None:
        for prescription in prescriptions:
            prescription.doctor = doctorName(prescription.doctor)
            prescription.hospital = hospitalName(prescription.hospital)
            if len(prescription.description) > 40:
                prescription.description = prescription.description[0:40] + ' ...'
    if reports is not None:
        for report in reports:
            if report.doctor is not None:
                report.doctor = doctorName(report.doctor)
            if len(report.description) > 40:
                report.description = report.description[0:40] + ' ...'

    context = {'prescriptions': prescriptions, 'reports': reports,
               'person': person, 'check': check, 'doctor': doctor}
    return render(request, "BackEndApp/allRecords.html", context)


def timelineData(id):
    data = []
    data2 = []
    try:
        prescriptions = Prescription.objects.filter(patient=id)
    except:
        prescriptions = None
    try:
        reports = LabReport.objects.filter(patient=id)
    except:
        reports = None
    if prescriptions is not None:
        for prescription in prescriptions:
            date = prescription.date
            year = date.year
            month = date.strftime("%B")
            found = False
            for d in data:
                if year == d[0]:
                    found = True
                    if month not in d:
                        d.insert(len(d), month)
            if not found:
                data.insert(len(data), [year, month])

    if reports is not None:
        for report in reports:
            date = report.date
            year = date.year
            month = date.strftime("%B")
            found = False
            for d in data:
                if year == d[0]:
                    found = True
                    if month not in d:
                        d.insert(len(d), month)
            if not found:
                data.insert(len(data), [year, month])
    data.sort()
    for d in data:
        d1 = d[:1]
        d2 = d[1:]
        month_lookup = list(month_name)
        d2.sort(key=month_lookup.index)
        for enrty in d2:
            d1.append(enrty)
        data2.insert(0, d1)
    return data2


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Doctor'])
def summary(request):
    if request.method == "GET":
        patient = Patient.objects.get(CNIC=request.user.username)
        context = {'patient': patient, 'check': True}
        return render(request, "BackEndApp/summary.html", context)

    else:
        id = request.POST['cnic']
        patient = None
        try:
            patient = Patient.objects.get(CNIC=id)
        except:
            messages.error(request, "Patient not found")
            return redirect('feed')
        doctor = Doctor.objects.get(license_No=request.user.username)
        context = {'patient': patient, 'doctor': doctor, 'check': False}
        return render(request, "BackEndApp/summary.html", context)


@login_required(login_url='login')
def profile(request):
    group = request.user.groups.all()
    group = str(group[0])
    id = request.user.username
    person = ""
    patient = False
    if group == 'Patient':
        patient = True
        person = Patient.objects.get(CNIC=id)

    if group == 'Doctor':
        person = Doctor.objects.get(license_No=id)

    if request.method == 'GET':
        context = {'person': person, 'patient': patient}
        return render(request, "BackEndApp/Profile.html", context)

    elif request.method == 'POST':
        try:
            phone = request.POST.get('phone')
        except:
            phone = patient.phone
        try:
            email = request.POST.get('email')
        except:
            email = person.email
        try:
            address = request.POST.get('address')
        except:
            address = person.address
        try:
            photo = request.FILES['photo']
            path = person.photo.name
        except:
            photo = person.photo
        if group == 'Patient':
            person = Patient.objects.get(CNIC=id)
            person.phone = phone
            person.photo = photo
            person.email = email
            person.address = address
            person.save()
        elif group == 'Doctor':
            person = Doctor.objects.get(CNIC=id)
            person.phone = phone
            person.photo = photo
            person.email = email
            person.address = address
            person.save()

        os.remove(path)
        context = {'person': person, 'patient': patient}
        return render(request, "BackEndApp/Profile.html", context)


@login_required(login_url='login')
def home(request):
    return redirect('login')


def doctorName(license):
    try:
        doctor = Doctor.objects.filter(license_No=license)
        doctor = doctor[0]
        doctor = doctor.fName + " " + doctor.lName
        if len(doctor) > 19:
            doctor = doctor[0:19]
            doctor = doctor + ' ...'
    except:
        doctor = "N/A"
    return doctor


def hospitalName(id):
    try:
        hospital = Hospital.objects.filter(license_No=id)
        hospital = hospital[0]
        hospital = hospital.name
        if len(hospital) > 18:
            hospital = hospital[0:18]
            hospital = hospital + '...'
    except:
        hospital = "N/A"
    return hospital


def graphData(prescriptions, reports):
    start_date = datetime.datetime.today()
    start_date = str(start_date).split(' ')[0]
    start_date = str(start_date)
    start_date = datetime.datetime.strptime(
        start_date, '%Y-%m-%d').date()
    delta = timedelta(days=1)
    i = 7
    visitcount = []
    while i > 0:
        doctor, lab = 0, 0
        if prescriptions:
            for prescription in prescriptions.iterator():
                if prescription.date == start_date:
                    doctor += 1
        if reports:
            for report in reports.iterator():
                if report.date == start_date:
                    lab += 1
        start = str(start_date)
        temp = datetime.datetime.strptime(
            start, '%Y-%m-%d').strftime("%d/%m/%Y")
        visitcount.insert(len(visitcount), [str(temp), doctor, lab])
        start_date -= delta
        i -= 1

    visitcount = [['Date', 'Visits to Doctor', 'Tests']] + visitcount
    return visitcount


@login_required(login_url='login')
def patientFeed(request, id):
    try:
        patient = Patient.objects.get(CNIC=id)
    except:
        u = User.objects.get(username=request.user.username)
        u.delete()
        messages.error(request, "No User Found")
        return redirect('login')
    prescriptions, reports = [], []
    try:
        prescriptions = Prescription.objects.filter(
            patient=request.user.username).order_by('-date')
        doctor = doctorName(prescriptions[0].doctor)
        hospital = hospitalName(prescriptions[0].hospital)
        date = prescriptions[0].date
    except:
        prescriptions = None
        doctor = 'N/A'
        hospital = 'N/A'
        date = 'N/A'

    try:
        reports = LabReport.objects.filter(
            patient=request.user.username).order_by('-date')
        laboratory = reports[0].laboratory
        label = reports[0].label
        labDate = reports[0].date

    except:
        reports = None
        laboratory = 'N/A'
        label = 'N/A'
        labDate = 'N/A'

    visitcount = graphData(prescriptions, reports)

    if prescriptions:
        prescriptions = prescriptions[0:3]
        for prescription in prescriptions:
            prescription.label = prescription.label[0:12]
            prescription.doctor = doctorName(prescription.doctor)[0:15]

    if reports:
        reports = reports[0:3]
        for report in reports:
            report.label = report.label[0:12]
            report.laboratory = report.laboratory[0:15]

    context = {'patient': patient,
               'prescriptions': prescriptions, 'reports': reports, 'doctor': doctor, 'hospital': hospital,
               'date': date, 'laboratory': laboratory, 'label': label,
               'labDate': labDate, 'vis': json.dumps(visitcount)}

    return render(request, 'BackEndApp/patientHomePage.html', context)


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Laboratory', 'Admin', 'Doctor', 'Hospital'])
def feed(request):
    group = request.user.groups.all()
    group = str(group[0])
    id = request.user.username
    if group == 'Patient':
        return patientFeed(request, id)

    if group == 'Laboratory':
        laboratory = Laboratory.objects.get(license_No=id)
        context = {'laboratory': laboratory}
        return render(request, 'BackEndApp/labHomePage.html', context)

    if group == 'Doctor':
        doctor = Doctor.objects.get(license_No=id)
        context = {'doctor': doctor}
        return render(request, 'BackEndApp/doctorHomePage.html', context)

    if group == 'Hospital':
        hospital = Hospital.objects.get(license_No=id)
        context = {'hospital': hospital}
        return render(request, 'BackEndApp/hospitalHomePage.html', context)

    if group == 'Admin':
        context = {'user': request.user}
        return render(request, 'BackEndApp/adminHomePage.html', context)


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
    hospital = Hospital.objects.get(license_No=request.user.username)
    context = {'hospital': hospital}
    return render(request, 'BackEndApp/hospitalHomePage.html', context)


@allowed_users(allowed=['Laboratory'])
def addLabReport(request):
    laboratory = Laboratory.objects.get(license_No=request.user.username)
    if request.method == "POST" and request.FILES['file']:
        file = request.FILES['file']
        patient = request.POST.get('patient')
        doctor = None
        try:
            Patient.objects.get(CNIC=patient)
        except:
            messages.error(request, "Incorrect Patient CNIC")
            return redirect('addLabReport')
        try:
            doctor = request.POST.get('doctor')
        except:
            doctor = "Self"
        label = request.POST.get('label')
        description = request.POST.get('description')
        date = request.POST.get('date')
        date = datetime.datetime.strptime(
            date, '%Y-%m-%d').strftime("%Y-%m-%d")
        x = LabReport(file=file, date=date, doctor=doctor, description=description,
                      patient=patient, label=label, laboratory=laboratory.name)
        x.save()
    context = {'laboratory': laboratory}
    return render(request, 'BackEndApp/labHomePage.html', context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')


def register(request):
    verification = False
    if request.method == 'POST':
        group = request.user.groups.all()
        try:
            group = str(group[0])
        except:
            group = 'Patient'

        if group == 'Admin':
            verification = True
        else:
            if request.user.is_authenticated:
                return redirect('feed')

        cnic = request.POST['cnic']
        password = request.POST['password']
        fname = request.POST['fname']
        lname = request.POST['lname']
        phone = request.POST['phone']
        email = request.POST['email']
        dob = request.POST['dob']
        address = request.POST['address']
        try:
            photo = request.FILES['file']
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
            z = Patient(CNIC=cnic, fName=fname, lName=lname,
                        dob=dob, phone=phone, address=address, email=email, photo=photo, user=x,
                        verification=verification)
            z.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('login')
        else:
            messages.error(
                request, "Already a patient found with same CNIC")
            return redirect('register')
    else:
        if request.user.is_authenticated:
            return redirect('feed')
        return render(request, 'BackEndApp/register.html')
