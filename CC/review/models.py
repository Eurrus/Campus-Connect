from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.utils import timezone
from datetime import timedelta
from qa.models import Answer,Question
from simple_history.models import HistoricalRecords
# Create your models here.
Q_Flags_Choices = [

    ('SPAM', 'Spam'), # Automatic = POST
    ('RUDE_OR_ABUSIVE', 'Rude or Abusive'), # Automatic = POST
    ('NOT_AN_ANSWER', 'Not an Answer'), # Only For Answer = ANSWER
    ('IN_NEED_OF_MODERATOR_INTERVATION', 'In Need of Moderator Intervation'), # Can only seen by moderators = POST
        # It needs a text field.
    # ('NEED_ADDITIONAL_DETAILS','Needs Additional Details'), # = QUESTION
    # ('NEED_TO_MORE_FOCUSED','Needs to be More Focused'), # Will be = QUESTION

    ('VERY_LOW_QUALITY', 'Very Low Quality'), # Will be pushed to Low Quality Posts = QUESTION


    ('NEEDS_IMPROVEMENT', 'Needs Improvement'),# = QUESTION
            ('DUPLICATE', 'Duplicate'), # ----Close Review----
            ('OPINION_BASED', 'Opinion Based'),# = QUESTION # ----Close Review----
            ('NEED_MORE_FOCUS', 'Need More Focus# = QUESTION'),# = QUESTION # ----Close Review----
            ('NEED_ADDITIONAL_DETAILS','Needs Additional Details'), # = QUESTION # ----Close Review----
        ('A_COMMUNITY_SPECIFIC_REASON', 'A Community specific reason'),# = QUESTION

            ('ABOUT_GENERAL_COMPUTING_HAR', 'About General'),# = QUESTION # ----Close Review----
            ('ABOUT_PROFESSIONAL', 'About Professional'),# = QUESTION # ----Close Review----
            ('SEEKING_RECCOMENDATIONS', 'Seeking Reccomendations'),# = QUESTION # ----Close Review----
            ('NEED_DEBUGGING', 'Need Debugging Details'),# = QUESTION # ----Close Review----
            ('NOT_REPRODUCIBLE', 'Not Reproducible'),# = QUESTION # ----Close Review----
            ('BLANTANLTY_OR_CLARITY', 'Blantanlity or Clarity'),# = QUESTION # ----Close Review----
]
class FlagPost(models.Model):
    flagged_by = models.ForeignKey(User, on_delete=models.CASCADE)
    question_forFlag = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True)
    answer_forFlag = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)
    actions_Flag_Q = models.CharField(max_length=300, choices=Q_Flags_Choices)

    how_many_votes_on_spamANDRude = models.IntegerField(default=0)
    how_many_votes_on_notAnAnswer = models.IntegerField(default=0)
    how_many_votes_on_others = models.IntegerField(default=0)

    flagged_at = models.DateTimeField(auto_now_add=True)
    ended = models.BooleanField(default=False)

    def __str__(self):
        return f"[WHY-FLAG] - {self.actions_Flag_Q}"
