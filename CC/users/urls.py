from . import views
from django.urls import path
app_name="users"

urlpatterns = [
	
	
	path('signup_view/',views.signup_view, name='signup_view'),
	
	path('logout_view/', views.logout_view, name='logout_view'),
	
	path('login_request/', views.login_request, name="login_request"),
	
	
]

