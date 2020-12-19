from django.core.files import storage
from django.db import connections, models
from django.core.validators import MinLengthValidator
from django.db.models.deletion import CASCADE
from django.db.models.expressions import F
from djongo.storage import GridFSStorage
from django.contrib.auth.models import User

# Create your models here.


class Patient(models.Model):
    id = models.CharField(max_length=13, primary_key=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    password = models.CharField(max_length=999, validators=[
                                MinLengthValidator(8)])
    age = models.IntegerField(default=0)
    phone = models.CharField(max_length=11, null=True,
                             validators=[MinLengthValidator(11)])
    address = models.CharField(max_length=999, null=True)
    email = models.CharField(max_length=100, null=True)
    photo = models.ImageField(default='image.jpeg', null=True, blank=True)
    verification = models.BooleanField(
        default=False)

    def __str__(self):
        return self.firstName+' '+self.lastName


class Contact(models.Model):
    person = models.ForeignKey(
        "Patient", related_name="person_himself", on_delete=CASCADE, null=False)
    contact = models.ForeignKey(
        "Patient", related_name="trustedContact", on_delete=CASCADE, null=False)

    def __str__(self):
        return str(self.person) + "'s trusted contact is "+str(self.contact)
