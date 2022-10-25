from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from . forms import SignUpForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from Profile.models import Profile
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import logout

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        # getFormEmail = form.cleaned_data['email']
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            getFormEmail = form.cleaned_data['email']
            branch=form.cleaned_data.get('branch')
            user= form.save()
            user = authenticate(username=username, password=raw_password)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.user.profile.email = getFormEmail
            request.user.profile.branch=branch
            return redirect('Profile:home')
    else:
        form = SignUpForm()
        print("Hello")
    return render(request, 'users/signup.html', {'form': form})

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.user.profile.logout_on_all_devices = False
                request.user.profile.save()
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request = request,
                    template_name = "users/login.html",
                    context={"form":form})

def logout_view(request):
    logout(request)
    print("you logged out")
    return redirect('Profile:home')

