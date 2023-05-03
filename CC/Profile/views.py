from django.shortcuts import render
from django.contrib.auth.models import User
from qa.models import Question
from django.http import HttpResponse,JsonResponse
from django.db import models
# Create your views here.
def home(request):
   objects=Question.objects.all()
#    print(objects)
   objects=sorted(objects,key = lambda obj: obj.calculate_UpVote_DownVote,reverse=True)
#    objects=sort(objects, key = lambda obj: obj.calculate_UpVote_DownVote)
#    print(objects)
   context={'questions':objects}
   return render(request, 'Profile/home.html',context)
def usersPage(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'profile/usersPage.html', context)
def error_Page(request):
    return render(request,'profile/error_Page.html')
def Ajax_searchUser(request):
    q = request.GET.get('w')
    results = User.objects.filter(username__icontains=q).distinct()
    serialized_results = []
    for result in results:
        serialized_results.append({
            'id': result.id,
            'user_name': result.username,
            })
    print(serialized_results)

    return JsonResponse({'results': serialized_results})