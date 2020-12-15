from django.db import models

# Create your models here.


class Person(models.Model):
    id = models.CharField(max_length=13, primary_key=True)
    firstName = models.CharField(max_length=30, null=True)
    lastName = models.CharField(max_length=30, null=True)
    age = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.firstName+' '+self.lastName
