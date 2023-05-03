from django.shortcuts import render
from django.contrib.auth.models import User
from qa.models import Question
from django.http import HttpResponse,JsonResponse
# Create your views here.
def home(request):
   questions = Question.objects.all()
#    sorted_results = sorted(questions, key= lambda q: q.calculate_UpVote_DownVote())
   context={'questions':questions}
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