from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('signout', views.signout, name="signout"),
    path('signin', views.signin, name="signin"), 
    path('activate/<uidb64>/<token>', views.activate, name="activate")
]