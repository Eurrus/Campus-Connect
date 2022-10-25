from django.contrib import admin
from django.urls import path,include

from . import views
app_name='qa'
urlpatterns=[
    path('new_question/', views.new_question, name='new_question'),
    path('questions/', views.questions, name='questions'),
    path('reviewQuestion/', views.reviewQuestion, name='reviewQuestion'),
]