from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
# Create your views here.
def home(request):
   context={}
   return render(request, 'Profile/home.html',context)
def usersPage(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'profile/usersPage.html', context)