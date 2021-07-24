import datetime
from calendar import month_name
from datetime import date, timedelta
from base64 import b64encode
from time import strptime
from cryptography.fernet import Fernet
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import json
from django.shortcuts import render
from BackEndApp.models import *
from .decorators import *
from .forms import *

thirty = ['04', '06', '09', '11']
thirtyOne = ['01', '03', '05', '07', '08', '10', '12']


def encrypt(file):
    filekey = open('filekey.txt', 'rb')
    key = filekey.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(file)
    encrypted = encrypted.decode(encoding='utf-8')
    return encrypted


def decrypt(bytes):
    filekey = open('filekey.txt', 'rb')
    bytes = bytes.encode(encoding='utf-8')
    key = filekey.read()
    fernet = Fernet(key)
    bytes = fernet.decrypt(bytes)
    encoded = b64encode(bytes)
    mime = "image/jpeg"
    encoded = str(encoded)[3:]
    uri = "data:%s;base64,%s" % (mime, encoded)
    return uri


def timeline(request):
    if request.method == 'POST':
        try:
            date = request.POST['q']
            date = date.split(' ')
            month = date[0]
            month = strptime(month, '%B').tm_mon
            if month < 10:
                month = '0' + str(month)
            if str(month) in thirtyOne:
                start = [date[1] + "-" + str(month) + "-" + '01']
                end = [date[1] + "-" + str(month) + "-" + '31']
            elif str(month) in thirty:
                start = [date[1] + "-" + str(month) + "-" + '01']
                end = [date[1] + "-" + str(month) + "-" + '30']
            else:
                if date[1] % 4 == 0:
                    start = [date[1] + "-" + str(month) + "-" + '01']
                    end = [date[1] + "-" + str(month) + "-" + '29']
                else:
                    start = [date[1] + "-" + str(month) + "-" + '01']
                    end = [date[1] + "-" + str(month) + "-" + '28']
            request.session['start'] = start
            request.session['end'] = end
            return viewFilterRecords(request)
        except:
            cnic = request.POST['cnic']
            request.session['cnic'] = cnic
            try:
                Patient.objects.get(CNIC=cnic)
            except:
                messages.error(request, "Invalid CNIC, Patient not found.")
                return redirect('feed')
            data = timelineData(cnic)
            if data == []:
                data = False
            user = Doctor.objects.get(license_No=request.user.username)
            text, sum = summary(cnic)
            context = {
                'text': text,
                'sum': sum,
                'patient': False,
                'data': data,
                'user': user
            }
            return render(request, "BackEndApp/timeline.html", context)
    else:
        user = Patient.objects.get(CNIC=request.user.username)
        text, sum = summary(user.CNIC)
        data = timelineData(user.CNIC)
        if not data:
            data = False
        context = {
            'text': text,
            'sum': sum,
            'patient': True,
            'data': data,
            'user': user
        }
        return render(request, "BackEndApp/timeline.html", context)


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Doctor'])
def viewFilterRecords(request):
    group = request.user.groups.all()
    group = str(group[0])

    if group == 'Patient':
        check = 1  # for patient
        user = Patient.objects.get(CNIC=request.user.username)
        patient = user
    else:
        try:
            cnic = request.POST['cnic']
            patient = Patient.objects.get(CNIC=cnic)
        except:
            try:
                cnic = request.session['cnic']
                patient = Patient.objects.get(CNIC=cnic)
            except:
                return redirect('feed')
        check = 2
        user = Doctor.objects.get(license_No=request.user.username)

    prescriptions = ""
    try:
        if request.session.has_key('start') and request.session.has_key('end'):
            prescriptions = Prescription.objects.filter(patient=patient.CNIC)
            prescriptions = prescriptions.filter(
                date__range=[request.session['start'][0], request.session['end'][0]])
        else:
            prescriptions = Prescription.objects.filter(patient=patient.CNIC)
    except:
        prescriptions = None
    try:
        if request.session.has_key('start') and request.session.has_key('end'):
            reports = LabReport.objects.filter(patient=patient.CNIC)
            reports = reports.filter(
                date__range=[request.session['start'][0], request.session['end'][0]])
        else:
            reports = LabReport.objects.filter(patient=patient.CNIC)
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
               'user': user, 'check': check, 'patient': patient}
    return render(request, "BackEndApp/allRecords.html", context)


def viewTrustedContact(request):
    person = None
    temp = Patient.objects.get(CNIC=request.user.username)
    if request.method == 'POST':
        try:
            request.POST['remove']
            temp.trustedContact = None
            temp.save()
            return redirect('viewTrustedContact')
        except:
            try:
                cnic = request.POST['CNIC']
                if cnic != temp.CNIC:
                    try:
                        person = Patient.objects.get(CNIC=cnic)
                        temp.trustedContact = cnic
                        temp.save()
                    except:
                        messages.error(
                            request, "Invalid CNIC, No user found with id: " + cnic + ".")
                else:
                    messages.error(
                        request, "Cannot add yourself as your trusted contact.")
            except:
                return render(request, "BackEndApp/trustedContact.html")
    else:
        try:
            person = Patient.objects.get(CNIC=temp.trustedContact)
        except:
            person = None
    context = {'patient': temp, 'person': person}
    return render(request, "BackEndApp/trustedContact.html", context)


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Doctor', 'Hospital', 'Laboratory'])
def viewAllRecords(request):
    group = request.user.groups.all()
    group = str(group[0])
    user = None
    patient = None
    check = 0

    if group == 'Patient':
        check = 1  # for patient
        user = Patient.objects.get(CNIC=request.user.username)
        patient = user
    elif group == 'Doctor':
        try:
            cnic = request.session['cnic']
            patient = Patient.objects.get(CNIC=cnic)
        except:
            return redirect('feed')
        check = 2  # for doctor
        user = Doctor.objects.get(license_No=request.user.username)
    elif group == 'Hospital':
        check = 3  # for hospital
        user = Hospital.objects.get(license_No=request.user.username)
        try:
            cnic = request.POST['cnic']
            try:
                patient = Patient.objects.get(CNIC=cnic)
            except:
                messages.error(request, 'Invalid CNIC, patient not found')
                return redirect('feed')
            request.session['cnic'] = cnic
            try:
                request.POST['newRecord']
                context = {'user': user}
                return render(request, "BackEndApp/newPrescription.html", context)
            except:
                None
        except:
            messages.error(
                request, "Invalid CNIC, Patient not found.")
            return redirect('feed')
    elif group == 'Laboratory':
        check = 3  # for lab
        user = Laboratory.objects.get(license_No=request.user.username)
        try:
            cnic = request.POST['cnic']
            try:
                patient = Patient.objects.get(CNIC=cnic)
            except:
                messages.error(request, 'Invalid CNIC, patient not found')
                return redirect('feed')
            request.session['cnic'] = cnic
            try:
                request.POST['newRecord']
                context = {'user': user}
                return render(request, "BackEndApp/newReport.html", context)
            except:
                None
        except:
            messages.error(
                request, "Invalid CNIC, Patient not found.")
            return redirect('feed')
    try:
        prescriptions = Prescription.objects.filter(patient=patient.CNIC)
    except:
        prescriptions = None
    try:
        reports = LabReport.objects.filter(patient=patient.CNIC)
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
    if group == 'Hospital':
        context = {'prescriptions': prescriptions,
                   'patient': patient, 'check': check, 'user': user}
        return render(request, "BackEndApp/addFollowUp.html", context)
    if group == 'Laboratory':
        context = {'reports': reports,
                   'patient': patient, 'check': check, 'user': user}
        return render(request, "BackEndApp/addFollowUp.html", context)
    else:
        context = {'prescriptions': prescriptions, 'reports': reports,
                   'patient': patient, 'check': check, 'user': user}
        return render(request, "BackEndApp/allRecords.html", context)


def getPrescriptionFiles(request):
    prescriptions = []
    serial = request.POST['serial']
    prescription = Prescription.objects.get(id=serial)
    if prescription.patient == request.user.username:
        user = Patient.objects.get(CNIC=prescription.patient)
        check = True
    else:
        user = Doctor.objects.get(license_No=request.user.username)
        check = False
    prescription.doctor = doctorName(prescription.doctor)
    prescription.hospital = hospitalName(prescription.hospital)
    files = PrescriptionFiles.objects.filter(serial=serial)
    for file in files:
        temp = {'label': file.label, 'description': file.description, 'file': file.file,
                'doctor': prescription.doctor, 'hospital': prescription.hospital, 'date': file.date}
        prescriptions.append(temp)

    context = {'prescriptions': prescriptions, 'user': user, 'check': check}
    return render(request, "BackEndApp/someRecords.html", context)


def getReportFiles(request):
    reports = []
    serial = request.POST['serial']
    report = LabReport.objects.get(id=serial)
    if report.doctor is not None:
        report.doctor = doctorName(report.doctor)
    files = ReportFiles.objects.filter(serial=serial)
    for file in files:
        temp = {'label': file.label, 'description': file.description, 'file': file.file,
                'doctor': report.doctor, 'laboratory': report.laboratory, 'date': file.date}
        reports.append(temp)
    context = {'reports': reports}
    return render(request, "BackEndApp/someRecords.html", context)


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


def hospitalCity(id):
    return Hospital.objects.get(license_No=id).city


def stats():
    diseases = ['Corona', 'Hepatitis', "Cancer", 'Diabetes', 'Heart']
    data = {'Lahore': dict.fromkeys(diseases, 0),
            'Islamabad': dict.fromkeys(diseases, 0),
            'Karachi': dict.fromkeys(diseases, 0),
            'Quetta': dict.fromkeys(diseases, 0),
            'Peshawar': dict.fromkeys(diseases, 0)}
    for disease in diseases:
        prescriptions = Prescription.objects.filter(
            label__icontains=disease)
        for prescription in prescriptions:
            if prescription.city == 'Lahore':
                data['Lahore'][disease] += 1
            elif prescription.city == 'Karachi':
                data['Karachi'][disease] += 1
            elif prescription.city == 'Peshawar':
                data['Peshawar'][disease] += 1
            elif prescription.city == 'Quetta':
                data['Quetta'][disease] += 1
            elif prescription.city == 'Islamabad':
                data['Islamabad'][disease] += 1
    return data


def cityAnalysis():
    city = 'Lahore'
    diseases = {}
    start = "2021-03-01"
    end = "2021-06-30"
    if start and end:
        prescriptions = Prescription.objects.filter(date__range=[start, end])
        if city:
            prescriptions = prescriptions.filter(city=city)
    else:
        prescriptions = Prescription.objects.all()
        if city:
            prescriptions = prescriptions.filter(city=city)
    for prescription in prescriptions:
        if diseases.get(prescription.label):
            diseases[prescription.label] += 1
        else:
            temp = {prescription.label: 1}
            diseases.update(temp)
    diseases = sorted(diseases.items(), key=lambda x: x[1], reverse=True)
    return diseases


def summary(cnic):
    name = Patient.objects.get(CNIC=cnic)
    text = name.fName + " " + name.lName + " had"
    try:
        prescriptions = Prescription.objects.filter(patient=cnic)
        prescriptions = prescriptions.filter(criticalLevel='Severe')
        prescriptions = sorted(
            prescriptions, key=lambda prescriptions: prescriptions.date, reverse=True)
    except:
        prescriptions = None
    try:
        reports = LabReport.objects.filter(patient=cnic)
        reports = reports.filter(criticalLevel='Severe')
        reports = sorted(
            reports, key=lambda reports: reports.date, reverse=True)
    except:
        reports = None
    data = []
    for prescription in prescriptions:
        data.append(prescription)
    for report in reports:
        data.append(report)
    data = sorted(
        data, key=lambda data: data.date, reverse=True)
    if not prescriptions and not reports:
        text = "No data found for " + name.fName + " " + name.lName
    else:
        temp = data[len(data)-1]
        days = (date.today() - temp.date).days
        years = days // 365
        months = (days - years * 365) // 30
        days = (days - years * 365 - months*30)
        years = str(years)
        months = str(months)
        days = str(days)
        if years != '0':
            if months != '0':
                text = "Over the course of "+years + " years and "+months+" months " + text
            else:
                text = "Over the course of " + years + " years " + text
        else:
            if months != '0':
                text = "Over the course of "+months+" months " + text
            else:
                text = "Over the course of "+days + " days " + text
        i = 1
        for d in data:
            if len(data) == 1:
                text += " " + d.description + "."
            elif i == len(data):
                text += " and " + d.description + "."
            else:
                text += " " + d.description + ","
            i += 1

    return text, data


@login_required(login_url='login')
@allowed_users(allowed=['Patient', 'Doctor'])
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
        image = None
        try:
            if not person.photo:
                person.photo = 'profile.jpg'
                person.save()
        except:
            pass
        context = {'person': person, 'patient': patient, 'image': image}
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
            try:
                if person.photo.name != 'C:/Users/Acer/MediLog/static/images/profile.jpg':
                    os.remove(person.photo.name)
            except:
                pass
        except:
            photo = person.photo
        #photo = encrypt(photo.file.read())
        if group == 'Patient':
            person = Patient.objects.get(CNIC=id)
            person.phone = phone
            person.photo = photo
            person.email = email
            person.address = address
            person.save()
        elif group == 'Doctor':
            person = Doctor.objects.get(license_No=id)
            person.phone = phone
            person.photo = photo
            person.email = email
            person.address = address
            person.save()
        try:
            if not person.photo:
                person.photo = 'profile.jpg'
                person.save()
        except:
            pass
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


def changePassword(request):
    if request.method == 'GET':
        return render(request, 'BackEndApp/changePassword.html')
    else:
        oldPassword = request.POST['oldPassword']
        newPassword = request.POST['newPassword']
        user = authenticate(
            request, username=request.user.username, password=oldPassword)
        if user is not None:
            try:
                user.set_password(newPassword)
                user.save()
                messages.success(request, 'Password changed successfully')
                login(request, user)
                return redirect('feed')
            except:
                messages.error(
                    request, 'Password not changed, choose a strong Password')
                return redirect('changePassword')
        else:
            messages.error(
                request, 'Incorrect old Password, Password not changed')
            return redirect('changePassword')


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
            prescription.label = prescription.label[0:10]
            prescription.doctor = doctorName(prescription.doctor)[0:15]

    if reports:
        reports = reports[0:3]
        for report in reports:
            report.label = report.label[0:10]
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
        user = Laboratory.objects.get(license_No=id)
        context = {'user': user}
        return render(request, 'BackEndApp/hospitalLandingPage.html', context)

    if group == 'Doctor':
        user = Doctor.objects.get(license_No=id)
        context = {'user': user}
        return render(request, 'BackEndApp/doctorHomePage.html', context)

    if group == 'Hospital':
        user = Hospital.objects.get(license_No=id)
        context = {'user': user}
        return render(request, 'BackEndApp/hospitalLandingPage.html', context)

    if group == 'Admin':
        data = cityAnalysis()
        data = stats()
        user = User.objects.get(username=request.user.username)
        user = user.first_name + " " + user.last_name
        context = {'user': user, 'data': data}
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


@login_required(login_url='login')
@allowed_users(allowed=['Hospital'])
def addPrescription(request):
    if request.method == "POST" and request.FILES['file']:
        files = request.FILES.getlist('file')
        patient = request.session['cnic']
        try:
            Patient.objects.get(CNIC=patient)
        except:
            messages.error(request, "Incorrect Patient CNIC")
            return redirect('addPrescription')
        doctor = request.POST['doctor']
        label = request.POST['label']
        try:
            Doctor.objects.get(license_No=doctor)
        except:
            messages.error(request, "Incorrect Doctor License Number")
            return redirect('addPrescription')
        hospital = request.user.username
        description = request.POST['description']
        date = request.POST['date']
        date = datetime.datetime.strptime(
            date, '%Y-%m-%d').strftime("%Y-%m-%d")
        severity = request.POST['severity']
        x = Prescription(date=date, description=description, criticalLevel=severity,
                         patient=patient, label=label, city=hospitalCity(hospital), doctor=doctor, hospital=hospital)
        x.save()
        for file in files:
            temp = PrescriptionFiles(
                serial=x.id, date=date, description=description, label=label, file=file)
            temp.save()
    hospital = Hospital.objects.get(license_No=request.user.username)
    context = {'user': hospital}
    return render(request, 'BackEndApp/hospitalLandingPage.html', context)


@allowed_users(allowed=['Laboratory'])
def addLabReport(request):
    laboratory = Laboratory.objects.get(
        license_No=request.user.username)
    if request.method == "POST" and request.FILES['file']:
        files = request.FILES.getlist('file')
        patient = request.session['cnic']
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
        severity = request.POST['severity']
        x = LabReport(date=date, doctor=doctor, description=description, criticalLevel=severity,
                      patient=patient, city=laboratory.city,
                      label=label, laboratory=laboratory.name)
        x.save()
        for file in files:
            temp = ReportFiles(serial=x.id, date=date,
                               description=description, label=label, file=file)
            temp.save()
    context = {'laboratory': laboratory}
    return render(request, 'BackEndApp/hospitalLandingPage.html', context)


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
            photo = 'C:/Users/Acer/MediLog/static/images/profile.jpg'
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


@login_required(login_url='login')
@allowed_users(allowed=['Admin'])
def registerDoctor(request):
    if request.method == 'POST':
        group = request.user.groups.all()
        try:
            group = str(group[0])
        except:
            group = 'Doctor'

        cnic = request.POST['cnic']
        password = request.POST['password']
        fname = request.POST['fname']
        lname = request.POST['lname']
        licenseNo = request.POST['licenseNo']
        phone = request.POST['phone']
        email = request.POST['email']
        address = request.POST['address']

        try:
            photo = request.FILES['file']
        except:
            photo = 'C:/Users/Acer/MediLog/static/images/profile.jpg'

        try:
            y = User.objects.get(username=licenseNo)
        except ObjectDoesNotExist:
            y = None
        if y is None:
            x = User.objects.create_user(
                username=licenseNo, first_name=fname, last_name=lname, password=password, email=email)
            x.save()
            try:
                group = Group.objects.get(name='Doctor')
            except:
                group = Group(name='Doctor')
                group.save()
                group = Group.objects.get(name='Doctor')
            x.groups.add(group)
            z = Doctor(CNIC=cnic, fName=fname, lName=lname, license_No=licenseNo,
                       phone=phone, address=address, email=email, photo=photo, user=x)
            z.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('feed')
        else:
            messages.error(
                request, "Already a doctor found with same license number")
            return redirect('feed')
    else:
        return render(request, 'BackEndApp/adminHomePage.html')


@login_required(login_url='login')
@allowed_users(allowed=['Admin'])
def registerHospital(request):
    if request.method == 'POST':
        group = request.user.groups.all()
        try:
            group = str(group[0])
        except:
            group = 'Hospital'

        name = request.POST['name']
        password = request.POST['password']
        licenseNo = request.POST['licenseNo']
        city = request.POST['city']
        branchCode = request.POST['branchCode']

        try:
            y = User.objects.get(username=licenseNo)
        except ObjectDoesNotExist:
            y = None
        if y is None:
            x = User.objects.create_user(
                username=licenseNo, first_name=name, password=password)
            x.save()
            try:
                group = Group.objects.get(name='Hospital')
            except:
                group = Group(name='Hospital')
                group.save()
                group = Group.objects.get(name='Hospital')
            x.groups.add(group)
            z = Hospital(name=name, license_No=licenseNo,
                         city=city, branch_code=branchCode, user=x)
            z.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('feed')
        else:
            messages.error(
                request, "Already a hospital found with same license number")
            return redirect('feed')
    else:
        return render(request, 'BackEndApp/adminHomePage.html')


@login_required(login_url='login')
@allowed_users(allowed=['Admin'])
def registerLab(request):
    if request.method == 'POST':
        group = request.user.groups.all()
        try:
            group = str(group[0])
        except:
            group = 'Laboratory'

        name = request.POST['name']
        password = request.POST['password']
        licenseNo = request.POST['licenseNo']
        city = request.POST['city']
        branchCode = request.POST['branchCode']

        try:
            y = User.objects.get(username=licenseNo)
        except ObjectDoesNotExist:
            y = None
        if y is None:
            x = User.objects.create_user(
                username=licenseNo, first_name=name, password=password)
            x.save()
            try:
                group = Group.objects.get(name='Laboratory')
            except:
                group = Group(name='Laboratory')
                group.save()
                group = Group.objects.get(name='Laboratory')
            x.groups.add(group)
            z = Hospital(name=name, license_No=licenseNo,
                         city=city, branch_code=branchCode, user=x)
            z.save()
            messages.success(request, 'Account Created Successfully')
            return redirect('feed')
        else:
            messages.error(
                request, "Already a hospital found with same license number")
            return redirect('feed')
    else:
        return render(request, 'BackEndApp/adminHomePage.html')


def followUpFiles(request):
    if request.method == 'POST' and request.FILES['file']:
        try:
            serial = request.session['serial']
            label = request.POST['label']
            description = request.POST['description']
            date = request.POST['date']
            files = request.FILES.getlist('file')
            group = request.user.groups.all()
            group = str(group[0])
            if group == 'Hospital':
                x = Prescription.objects.get(id=serial)
                for file in files:
                    x = PrescriptionFiles(
                        serial=serial, date=date, description=description, label=label, file=file)
                    x.save()
            else:
                x = LabReport.objects.get(id=serial)
                for file in files:
                    x = ReportFiles(
                        serial=serial, date=date, description=description, label=label, file=file)
                    x.save()
        except:
            return redirect('feed')
    return redirect('feed')


def addFollowUp(request):
    if request.method == 'POST':
        serial = request.POST['serial']
        request.session['serial'] = serial
        return render(request, 'BackEndApp/followUpForm.html')


def about(request):
    group = request.user.groups.all()
    group = str(group[0])
    context = {}
    user = None
    if group == 'Patient':
        user = Patient.objects.get(CNIC=request.user.username)
        context = {'patient': True, 'doctor': False, 'laboratory': False,
                   'admin': False, 'hospital': False, 'user': user}
    if group == 'Doctor':
        user = Doctor.objects.get(license_No=request.user.username)
        context = {'patient': False, 'doctor': True, 'laboratory': False,
                   'admin': False, 'hospital': False, 'user': user}
    if group == 'Laboratory':
        user = Laboratory.objects.get(license_No=request.user.username)
        context = {'patient': False, 'doctor': False, 'laboratory': True,
                   'admin': False, 'hospital': False, 'user': user}
    if group == 'Admin':
        user = User.objects.get(username=request.user.username)
        user = user.first_name + " " + user.last_name
        context = {'patient': False, 'doctor': False, 'laboratory': False,
                   'admin': True, 'hospital': False, 'user': user}
    if group == 'Hospital':
        user = Hospital.objects.get(license_No=request.user.username)
        context = {'patient': False, 'doctor': False, 'laboratory': False,
                   'admin': False, 'hospital': True, 'user': user}
    return render(request, 'BackEndApp/about.html', context)


@allowed_users(allowed=['Patient'])
def viewConnections(request):
    if request.method == 'GET':
        connections = Patient.objects.filter(
            trustedContact=request.user.username)
        context = {'connections': connections}
        return render(request, 'BackEndApp/connections.html', context)
    else:
        cnic = request.POST['cnic']
        request.session['cnic'] = cnic
        try:
            Patient.objects.get(CNIC=cnic)
        except:
            messages.error(request, "Invalid CNIC, Patient not found.")
            return redirect('viewConnections')
        data = timelineData(cnic)
        if data == []:
            data = False
        person = Patient.objects.get(CNIC=request.user.username)
        text, sum = summary(cnic)
        context = {
            'text': text,
            'sum': sum,
            'patient': False,
            'data': data,
            'person': person
        }
        return render(request, "BackEndApp/timeline.html", context)


def sendMessage(request):

    senderID = request.user.username
    receiverID = request.POST['uID']
    messageText = request.POST['text']
    x = Message(sender=senderID, receiver=receiverID, text=messageText)
    x.save()
    return redirect('loadSenders')


def loadMessages(request):
    receiverID = request.user.username
    messages = Message.objects.filter(receiver=receiverID)
    return redirect('feed')


def loadSenders(request):
    receiverID = request.user.username
    chatPeople = []
    messages = Message.objects.filter(receiver=receiverID)
    for message in messages:
        user = Patient.objects.get(CNIC=message.sender)
        if user not in chatPeople:
            chatPeople.append(user)

    messages = Message.objects.filter(sender=receiverID)
    for message in messages:
        user = Patient.objects.get(CNIC=message.receiver)
        if user not in chatPeople:
            chatPeople.append(user)

    context = {'chatPeople': chatPeople}
    return render(request, 'BackEndApp/chat.html', context)
