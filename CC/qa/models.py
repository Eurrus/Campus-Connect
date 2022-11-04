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
    is_deleted = models.BooleanField(default=False)
    print(tags)
    class Meta:
        ordering = ["-date"]
    def __unicode__(self):
     return  self.body
    def get_absolute_url(self):
        # 'slug':self.slug})
        return reverse('qa:questionDetailView', kwargs={'pk': self.pk, })
class Answer(models.Model):
    answer_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    questionans = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    body = MartorField()
    a_vote_ups = models.ManyToManyField(User, related_name='a_vote_up', blank=True)
    a_vote_downs = models.ManyToManyField(User, related_name='a_vote_down', blank=True)
    accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)