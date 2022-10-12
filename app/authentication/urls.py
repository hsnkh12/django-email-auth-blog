from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from .views import RegisterView, LoginView, ActivateEmailView

app_name = "authentication"

urlpatterns = [

    path("",TemplateView.as_view(template_name = "registration/is_auth.html"), name="index"),
    path("register/",RegisterView.as_view(),name="register"),
    path("login/",LoginView.as_view(),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("activate/<uidb64>/<token>",ActivateEmailView,name="activate"),
   
]