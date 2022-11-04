from django.contrib import admin
from django.urls import path,include

from . import views
app_name='qa'
urlpatterns=[
    path('new_question/', views.new_question, name='new_question'),
    path('questions/', views.questions, name='questions'),
    path('reviewQuestion/', views.reviewQuestion, name='reviewQuestion'),
    path('questionDetailView/<int:pk>/', views.questionDetailView, name='questionDetailView'),
    path('delete_answer/<int:answer_id>/', views.delete_answer, name='delete_answer'),
    path('undelete_answer/<int:answer_id>/', views.undelete_answer, name='undelete_answer'),
]