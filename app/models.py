import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .constants import *

# Create your models here.

class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    username = None
    password = models.CharField(max_length=100)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3 )
    device_token = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_notification = models.BooleanField(default=False)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    

class Car(models.Model):
    creation_date = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    numero_voiture=models.PositiveSmallIntegerField()
    name = models.CharField(max_length=30)
    plate_number = models.CharField(max_length=30,unique=True)
    gpsdevice = models.ForeignKey('GpsDevices',on_delete=models.CASCADE,related_name='gps',blank=True,null=True)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)    
    is_deleted = models.BooleanField(default=False)
  
    def __str__(self):
        return self.plate_number
    
    
class GpsDevices(models.Model):
    creation_date = models.DateTimeField(auto_now=True)
    imei = models.CharField(max_length=20,unique=True,primary_key=True)
    phone_number = models.CharField(max_length=14,unique=True)
    operator = models.PositiveIntegerField(choices=OPERATOR,default=1)
    is_ignited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

class TrackerData(models.Model):
    imei = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data = models.JSONField()

    def __str__(self):
        return self.imei