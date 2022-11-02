from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from martor.models import MartorField
from django.urls import reverse
# Create your models here.
class Question(models.Model):
    post_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=5000, default='')
    body = MartorField()
    tags = TaggableManager()
    date = models.DateTimeField(auto_now_add=True)
    print(tags)
    class Meta:
        ordering = ["-date"]
    def __unicode__(self):
     return  self.body
    def get_absolute_url(self):
        # 'slug':self.slug})
        return reverse('qa:questionDetailView', kwargs={'pk': self.pk, })