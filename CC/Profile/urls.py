from django.contrib import admin
from django.urls import path,include

from . import views
app_name='Profile'
urlpatterns=[
    path('',views.home,name="home"),
    path('usersPage/', views.usersPage, name='usersPage'),
 ]