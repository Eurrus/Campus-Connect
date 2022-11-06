from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse
# Create your views here.
def home(request):
   context={}
   return render(request, 'Profile/home.html',context)
def usersPage(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'profile/usersPage.html', context)
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