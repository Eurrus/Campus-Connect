from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from martor.models import MartorField
from django.urls import reverse
from simple_history.models import HistoricalRecords
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
    @property
    def calculate_UpVote_DownVote(self):
        get_Upvotes = self.qupvote_set.count()
        get_DownVotes = self.qdownvote_set.count()
        print(get_Upvotes - get_DownVotes)
        return get_Upvotes - get_DownVotes
    def get_absolute_url(self):
        # 'slug':self.slug})
        return reverse('qa:questionDetailView', kwargs={'pk': self.pk, })
class QUpvote(models.Model):
    upvote_by_q = models.ForeignKey(User, on_delete=models.CASCADE)
    upvote_question_of = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    hisory = HistoricalRecords(related_name="qupvotehistory")

    def __str__(self):
        return f"{self.upvote_question_of} = [UPVOTED-BY] {self.upvote_by_q}"
class Answer(models.Model):
    answer_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    questionans = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    body = MartorField()
    a_vote_ups = models.ManyToManyField(User, related_name='a_vote_up', blank=True)
    a_vote_downs = models.ManyToManyField(User, related_name='a_vote_down', blank=True)
    accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    @property
    def countAllTheVotes(self):
        return self.a_vote_ups.all().count() - self.a_vote_downs.all().count()
class QDownvote(models.Model):
    downvote_by_q = models.ForeignKey(User, on_delete=models.CASCADE)
    downvote_question_of = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    hisory = HistoricalRecords(related_name="qdownvotehistory")

    def __str__(self):
        return f"{self.downvote_question_of} = [DOWNVOTED-BY] {self.downvote_question_of}"