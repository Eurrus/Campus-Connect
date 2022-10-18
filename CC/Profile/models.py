from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=30, default='')
    not_to_Display_Full_name = models.CharField(max_length=30, default='')
    email = models.EmailField(max_length=30, default='')
    location = models.CharField(max_length=30, default='')
    title = models.CharField(max_length=30, default='')
