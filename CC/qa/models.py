from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from martor.models import MartorField
# Create your models here.
class Question(models.Model):
    post_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=5000, default='')
    body = MartorField()
    tags = TaggableManager()
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-date"]