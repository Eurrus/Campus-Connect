from wsgiref.validate import validator
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator
# Create your models here.
from django.dispatch import receiver
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',default = "")
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    #full_name = models.CharField(max_length=30, default='')
    #username=models.CharField(max_length=30,default='')
    #not_to_Display_Full_name = models.CharField(max_length=30, default='')
    email = models.EmailField(max_length=30, default='')
    # location = models.CharField(max_length=30, default='')
    # title = models.CharField(max_length=30, default='')
    branch=models.CharField(max_length=4,default='')
    enrollmentid=models.CharField(validators=[RegexValidator(r'^BT\d{2}\w{3,4}\d{3}$')],max_length=10,default='BT19CSE000')
    mobile=PhoneNumberField(null = False, blank = False,default='1111111111')
    studentId=models.IntegerField(null = False, blank = False,default=10000,validators=[MaxValueValidator(99999),MinValueValidator(10000)])
    create_tags = models.BooleanField(default=False)
@receiver(post_save, sender=User)  # add this
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)  # add this
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()