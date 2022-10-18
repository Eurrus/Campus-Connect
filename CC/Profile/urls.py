from django.contrib import admin
from django.urls import path,include

from . import views
app_name='Profile'
urlpatterns=[
    path('',views.base,name="base")
 ]