from django.contrib import admin
from django.urls import path,include

from . import views
app_name='Profile'
urlpatterns=[
    path('',views.home,name="home"),
    path('usersPage/', views.usersPage, name='usersPage'),
    path('Ajax_searchUser/', views.Ajax_searchUser, name='Ajax_searchUser'),
    path('error',views.error_Page,name='error_Page'),
 ]