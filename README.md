# django-email-auth-blog 

How to login/register with email instead of username in Django

blog url -> https://hassanelabdallah.hashnode.dev/how-to-loginregister-with-email-instead-of-username-in-django



# Introduction
  As we all know, for Django's default user model, the user identifier is the username, which makes the username field required for login and registering. Sometimes, logging in with Email could be a better approach, as it adds some security. For example, two-factor authentication at password reset. 
In this tutorial, I am going to show you how to login/register with Email, and how to send Email confirmation to activate an account.
Before we start, you can find this project on my [Github repository](https://github.com/hsnkh12/django-email-auth-blog). Now let’s get started ;)





# Implementation


### Part 1: Create a Django project 

1- Create a new directory and move inside it.

```
$ mkdir Django_email_auth
$ cd Django_email_auth
``` 

2- Create a new virtual environment and activate it.

```
$ python3 -m venv venv
$ source venv/bin/activate
``` 

3- Install Django.

```
$ pip3 install django
``` 

4- Start new Django project and move inside it.

```
$ django-admin startproject app 
$ cd app
``` 

5- Create new app.

```
$ python3 manage.py startapp authentication
``` 

6- Create templates directory.

```
$ mkdir templates
``` 

7- Files structure will be as follows: 

```
.
├── app
│   ├── app
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── authentication
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── db.sqlite3
│   ├── manage.py
│   └── templates
└── venv

```

### Part 2: Setting up the project

1- Go to **app/app/settings.py** and add todos app to INSTALLED_APPS to use it in the project.

```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

		# Add this line 
    'authentication'
]
```

2- Go to **app/app/settings.py** and add templates Directory in TEMPLATES DIRS to use html templates in views. 

```
import os
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
				# Add this line
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

3- Go to **app/authentication/models.py** and define User model. We have to import and inherit Django's ```AbstractUser``` class. It provides the full implementation of the default User as an abstract model. Now we add the following:

```
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    username = models.CharField(
        primary_key=False, 
        max_length = 150
    )
    
    email = models.EmailField(
        max_length= 100,
        unique= True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
```
id is going to be UUID field instead of Django's default Integer id field. This implementation is totally optional. For the username field, primary key will be false to identify user by **id** instead of username.
Last two lines, we are giving Email field the priority to be required in login/register instead of username.



4- Next, let's refer to this user model as our auth model, by going to **app/app/settings.py** and add the following:

```
AUTH_USER_MODEL = "authentication.user"
```

5- Create **forms.py** file in **app/authentication**. Get inside it and let's create our user creation form using Django's ```UserCreationForm``` class.

```
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CreateUserForm(UserCreationForm):

    class Meta:
        model=User
        fields=['email','password1','password2']
``` 
Fields are optional, you can add more fields if you want. But let's just keep it simple with email and password.

6- Go to **app/authentication/admin.py**, and let's register our user model in admin

```
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin 
from.forms import CreateUserForm
# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CreateUserForm

admin.site.register(User,CustomUserAdmin)
```

6- Apply the migrations to create the tables in the sqlite3 database.

```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
``` 



### Part 3: Email sending setup

1- Now, let's add **Send email confirmation** feature. Before we start, install cryptography and django util six package.

```
$ pip3 install django-cryptography
``` 

```
$ pip3 install django-utils-six
``` 


2- Create **tokens.py** file in **app/authentication**. Get inside it and let's create our **TokenGenerator** class using Django's ```PasswordResetTokenGenerator``` class.

```
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
``` 
Now every time user wants to register, a unique token will be generated immediately using this class, which is used to create a link with our domain name, and will be sent to user's email.

3- Next, create **emails.py** file in **app/authentication**. Get inside it and let's create our **send_activation_mail** function using Django's ```send_mail``` function.

```
from django.core.mail import send_mail
from cryptography.fernet import Fernet
from django .conf import settings
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import TokenGenerator
from django.utils.encoding import force_bytes
from django.apps import apps


def send_activation_mail(**kwargs):

	# Get user model
    UserModel = apps.get_model('authentication','User')
	# Get intended user by userID
    user = UserModel.objects.get(pk=kwargs['userID'])
	# Create TokenGenerator object
    account_activation_token = TokenGenerator()

    context = {
        'user':user, 
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
		# Create activation token and pass it to the HTML template
        'token': account_activation_token.make_token(user)         
		}

    html_content = render_to_string('registration/email_confirm.html',context)

    mail = {
        'subject' : "Email Confirmation",
        'message' : None,
        'html_message' : html_content,
        'from_email' : settings.EMAIL_HOST_USER,
    }

    send_mail(**mail,fail_silently=True, recipient_list= [user.email])

    return
``` 
This function will be responsible for sending email confirmation message to user's email, provided with activation link, which generated by our ```TokenGenerator``` class.

5- Now, Go to **app/app/settings.py** and setup your email information.

```
EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.DOMAIN.com' # Add your smtp server here
EMAIL_USE_TLS = True
EMAIL_PORT = 587 # Add email's port here
EMAIL_HOST_USER = ' ' # Add your email here
EMAIL_HOST_PASSWORD = ' ' # Add your password here
``` 
Make sure that your information is correct. Otherwise, there will be an error when calling ```send_activation_mail``` function, and activation mail will not be sent to user's email.


### Part 4: Adding views and urls

1- Now, go to **app/authentication/views.py** and let's build our views.

2- Let's start with our first feature, which is **Login view**. For this view, we are going to use and inherit Django's ```LoginView``` auth class.

```
from django.contrib.auth.views import LoginView

class LoginFormView(LoginView):
    
    template_name = 'registration/login.html'
    success_url = '/'
``` 

3- Next, Let's create our **Register view**. For this view, we are going to use Django's generic ```View``` class. 

**GET request:**

```
from django.shortcuts import render,redirect
from .form import CreateUserForm
from django.views.generic import View

class RegisterView(View):

    def get(self,request):

        if not request.user.is_authenticated:
            
            form = CreateUserForm()
            context = {"form":form}
            return render(request,"registration/register.html",context)

        return redirect("/")
``` 

**POST request:**

```
from django.shortcuts import render,redirect
from .form import CreateUserForm
from django.views.generic import View
from .emails import send_activation_mail

class RegisterView(View):
  
  def get(self, request): ....

  def post(self,request):
        
        form = CreateUserForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Send activation email
            send_activation_mail(userID=str(user.id))

            return render(request,"registration/wait_email_confirmation.html",)

        
        context = {"form":form}
        return render(request,"registration/register.html",context)

``` 
When user is created, their account will be inactive, unless they activate their email with the activation link sent to their email. Note that this approach of sending emails is not the best, it's better to use [Django celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) or [Django mailer](https://pypi.org/project/django-mailer/) to send emails. But we are keeping it simple here, for you to understand the core concepts of this blog.

4- Next, let's create our **Activate email view**.

```
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .tokens import TokenGenerator
from django.http import HttpResponse
from django.contrib.auth import login
from .models import User

def ActivateEmailView(request, uidb64, token):

    account_activation_token = TokenGenerator()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'registration/email_confirmed.html')
    else:
        return HttpResponse('Activation link is invalid!')
``` 
This view will be responsible for checking the activation link if it's valid. If it is, it will automatically activate user's account and log them in. Otherwise, it will return 'Activation link is invalid!' http response, and user's account will not be activated unless they check the activation link sent to their email.

5- Overview of **app/authentication/views.py** file:

```
from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView
from .forms import CreateUserForm
from django.views.generic import View
from .emails import send_activation_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .tokens import TokenGenerator
from django.http import HttpResponse
from django.contrib.auth import login
from .models import User

class LoginFormView(LoginView):
    
    template_name = 'registration/login.html'
    success_url = '/'


class RegisterView(View):


    def get(self,request):

        if not request.user.is_authenticated:
            
            form = CreateUserForm()

            context = {"form":form}
            return render(request,"registration/register.html",context)

        return redirect("/")


    def post(self,request):
        
        form = CreateUserForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_activation_mail(userID=str(user.id))

            return render(request,"registration/wait_email_confirmation.html",)

        
        context = {"form":form}
        return render(request,"registration/register.html",context)


def ActivateEmailView(request, uidb64, token):

    account_activation_token = TokenGenerator()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'registration/email_confirmed.html')
    else:
        return HttpResponse('Activation link is invalid!')
``` 

6- Go to **app/app/settings.py** and add login and logout redirect urls.

```
LOGOUT_REDIRECT_URL = "/auth/"
LOGIN_REDIRECT_URL = "/auth/"
``` 


7- Now, let's create **urls.py** file in **app/authentication** to add our routes.

```
from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import RegisterView, LoginView

app_name = "authentication"

urlpatterns = [

    path("register/",RegisterView.as_view(),name="register"),
    path("login/",LoginView.as_view(),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
   
]
``` 
For **Logout view**, we used Django's ```LogoutView``` class.

8- Now for the last step in this part, let's connect our app urls. Go to **app/app/urls.py** and add the following:

```
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('authentication.urls')),
    path('',TemplateView.as_view(template_name='index.html'), name='index')
]
``` 



### Part 5: Adding HTML templates

1- Now for the final part, let's create our HTML templates to test our views. You can create your own UI and styles, but we are keeping it simple here for you to focus on the core concepts of this blog.

2- Go to **app/templates** and create the following:

**index.html**

  ```
  {% extends "base.html" %}
  
  {% block content %}
  
      <a href="{% url 'authentication:index' %}">Authentication app</a>
  
  {% endblock content %}
  ```

**base.html**

 ```
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>To-Do app</title>
  </head>
  <body>
  
      <nav>
          <!-- Add your Navbar here-->
      </nav>
  
  
      {% block content %}
      {% endblock content %}
  
      <footer>
          <!-- Add your Footer here-->
      </footer>
  
  </body>
  </html>
 ```


3- Create **registration/** folder in **app/templates/**. Get inside it and create the following:

**email_confirmation.html**

```
<a href="https://localhost:8000{% url 'authentication:activate' uidb64=uid token=token %}" >Confirm Account</a>
``` 

**email_confirmed.html**

```
{% extends "base.html" %}

{% block content %}

<h1>Thank you for confirming your email</h1>
<a href="/">Get back home</a>

{% endblock content %}
``` 

**is_auth.html**

```
{% extends "base.html" %}

{% block content %}

{% if user.is_authenticated %}

<h1>User is authenticated</h1>
<a href="{% url 'authentication:logout' %}">Logout</a>
{% else %}

<h1>User is not authenticated</h1>
<a href="{% url 'authentication:login' %}">Login</a>
<br>
<a href="{% url 'authentication:register' %}">Register</a>
{% endif %}

{% endblock content %}
``` 

**login.html**

```
{% extends "base.html" %}

{% block content %}

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p}}
        <button type="submit">Login</button>
        <a href="{% url 'authentication:register' %}">don't have an account? Sign up</a>


    </form>

{% endblock content %}
``` 

**register.html**

```
{% extends "base.html" %}

{% block content %}

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p}}
        <button type="submit">Register</button>
        <a href="{% url 'authentication:login' %}">Already have an account? Sign in</a>


    </form>

{% endblock content %}
``` 

**wait_email_confirmation.html**

```
{% extends "base.html" %}

{% block content %}
<p>Check your mailbox and confirm your email</p>
{% endblock content %}
``` 


And now you have an authentication app with email login/register, and email activation.

I tried to give you a brief explanation of basic authentication concepts in Django, and how to send activation link to the user. I hope this tutorial has benefited you. If it did, you can take this blog as a reference to using those approaches in your apps. Thank you for your time, and don't forget that You can find this project on my [Github repository](https://github.com/hsnkh12/django-email-auth-blog) . Good luck :)
