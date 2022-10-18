from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def base(request):
   context={}
   return render(request, 'Profile/base.html',context)