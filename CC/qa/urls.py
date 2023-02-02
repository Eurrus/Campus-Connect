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
    path('deleteQuestion/<int:question_id>/', views.deleteQuestion, name='deleteQuestion'),
	path('undeleteQuestion/<int:question_id>/', views.undeleteQuestion, name='undeleteQuestion'),
    path('edit_answer/<int:answer_id>/', views.edit_answer, name='edit_answer'),
    path('edit_question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('question_upvote_downvote/<int:question_id>/', views.question_upvote_downvote, name='question_upvote_downvote'),
    path('AjaxFlagForm/<int:question_id>/', views.AjaxFlagForm, name='AjaxFlagForm'),
    path('answer_upvote_downvote/<int:answer_id>/', views.answer_upvote_downvote, name='answer_upvote_downvote'),
    path('searchQuestion', views.searchQuestion, name='searchQuestion'),
]