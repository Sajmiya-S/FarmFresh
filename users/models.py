from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    customer = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15,blank=True,null=True) 

    def __str__(self):
        return self.customer.username

class Address(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,blank = True,null = True)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15,blank=True,null=True)
    house_no = models.CharField(max_length=20)
    street = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    pin = models.CharField(max_length=6,blank=True,null=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    name = models.CharField()
    email = models.EmailField()
    phone = models.CharField()
    message = models.TextField()

    def __str__(self):
        return self.name