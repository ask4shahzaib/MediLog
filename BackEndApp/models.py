import os
from django.contrib.auth.models import User
from MediLog.settings import BASE_DIR
from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models.deletion import CASCADE


# Create your models here.


def patient_profile(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.CNIC, ext)
    return os.path.join(BASE_DIR, 'static/images/patient_profile', filename)


def doctor_profile(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.CNIC, ext)
    return os.path.join(BASE_DIR, 'static/images/doctor_profile', filename)


def prescriptions(instance, filename):
    return os.path.join(BASE_DIR, 'static/images/prescriptions', filename)


def reports(instance, filename):
    return os.path.join(BASE_DIR, 'static/images/reports', filename)


class Patient(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=CASCADE)
    CNIC = models.CharField(max_length=13, primary_key=True)
    fName = models.CharField(max_length=30)
    lName = models.CharField(max_length=30)
    dob = models.DateField()
    trustedContact = models.CharField(max_length=13)
    phone = models.CharField(max_length=11, null=True,
    validators=[MinLengthValidator(11)])
    address = models.CharField(max_length=999, null=True)
    email = models.CharField(max_length=100, null=True)
    photo = models.ImageField(
        upload_to=patient_profile, default='profile.jpg', null=True, blank=True)
    verification = models.BooleanField(
        default=False)
    objects = models.Manager()

    def __str__(self):
        return self.fName+' '+self.lName


class Doctor(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=CASCADE)
    CNIC = models.CharField(max_length=13)
    fName = models.CharField(max_length=30)
    lName = models.CharField(max_length=30)
    license_No = models.CharField(max_length=20, null=False, primary_key=True)
    phone = models.CharField(max_length=11, null=True,
                             validators=[MinLengthValidator(11)])
    address = models.CharField(max_length=999, null=True)
    email = models.CharField(max_length=100, null=True)
    photo = models.ImageField(upload_to=doctor_profile,
                              default="profile.jpg", null=True, blank=True)
    verification = True
    objects = models.Manager()

    def __str__(self):
        return self.fName+' '+self.lName


class Laboratory(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=CASCADE)
    name = models.CharField(max_length=999)
    city = models.TextField()
    license_No = models.TextField(primary_key=True)
    branch_code = models.IntegerField()
    verification = True
    objects = models.Manager()

    def __str__(self):
        return self.name


class Hospital(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=CASCADE)
    name = models.CharField(max_length=999)
    city = models.TextField()
    license_No = models.TextField(primary_key=True)
    branch_code = models.IntegerField()
    verification = True
    objects = models.Manager()

    def __str__(self):
        return self.name


class Prescription(models.Model):
    label = models.CharField(max_length=30, null=False)
    date = models.DateField()
    criticalLevel = models.TextField()
    description = models.CharField(max_length=99999)
    patient = models.CharField(max_length=99)
    doctor = models.CharField(max_length=99)
    city = models.CharField(max_length=99)
    hospital = models.CharField(max_length=99)
    objects = models.Manager()

    def __str__(self):
        return self.description


class PrescriptionFiles(models.Model):
    serial = models.TextField()
    label = models.CharField(max_length=30, null=False)
    date = models.DateField()
    description = models.CharField(max_length=99999)
    file = models.FileField(upload_to=prescriptions)


class ReportFiles(models.Model):
    serial = models.TextField()
    label = models.CharField(max_length=30, null=False)
    date = models.DateField()
    description = models.CharField(max_length=99999)
    file = models.FileField(upload_to=reports)


class LabReport(models.Model):
    label = models.CharField(max_length=30, null=False)
    date = models.DateField()
    criticalLevel = models.TextField()
    city = models.CharField(max_length=99)
    doctor = models.CharField(max_length=99)
    description = models.CharField(max_length=99999)
    patient = models.CharField(max_length=99)
    laboratory = models.CharField(max_length=99)
    objects = models.Manager()

    def __str__(self):
        return self.description


class Message(models.Model):
    sender = models.CharField(max_length=30, null=False)
    receiver = models.CharField(max_length=30, null=False)
    text = models.CharField(max_length=300, null=False)
