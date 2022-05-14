import random
from django.shortcuts import render
from django.http import HttpResponse, request
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from workout import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str 
from . tokens import generate_token
from django.urls import reverse

display_images = [1, 2, 3, 4, 5, 6, 7, 8, 9]
gradients = ["background-color: #8BC6EC;background-image: linear-gradient(135deg, #8BC6EC 0%, #9599E2 100%);",
"background-color: #4158D0;background-image: linear-gradient(43deg, #4158D0 0%, #C850C0 46%, #FFCC70 100%);",
"background-image: linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12);",
"background-color: #FFDEE9;background-image: linear-gradient(0deg, #FFDEE9 0%, #B5FFFC 100%);",
]


# Create your views here.
def home(request):
    return render(request, "auth/index.html")

def signup(request):
    
    context = {
        'display_image' : "animations/"+str(random.choice(display_images))+".gif",
        'gradient' : gradients[random.choice([x for x in range(4)])],
    }

    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
    
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists!!")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!!")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 charaters!!")
            # return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!!")
            # return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
            
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your account has been successfully created.")
        
        # Welcome Email
        sub = "Welcome to Workout Assistant!!"
        msg = "Hello "+myuser.first_name+"!!\n"+"Welcome to Workout Assistant!! \nThankyou for visiting our website.\nWe have also send you a confirmation email, please confirm your email address in order to activate your accout. \n\nThanking You\nManik"
        from_email = settings.EMAIL_HOST_USER
        to_email = [myuser.email]
        send_mail(sub, msg, from_email, to_email, fail_silently=False)
        
        # Email address confirmation email
        current_site = get_current_site(request)
        sub_2 = "Confirm your email @ Workout-assistant Login!!"
        msg_2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            sub_2, 
            msg_2, 
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        # print(reverse('signup') + '#register')
        # return (reverse('signup') + '#register')
        return redirect("signin")
    
    # return (reverse('signup') + '#register')
    return render(request, "auth/signup.html", context)

def signin(request):
    
    context = {
        'display_image' : "animations/"+str(random.choice(display_images))+".gif",
        'gradient' : gradients[random.choice([x for x in range(4)])],
    }
    
    if request.method == "POST":
        username = request.POST["username"]
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "auth/index.html", {'fname':fname})
            
        else:
            messages.error(request, "BAD Credentials!!")
            return redirect("home")
    
    return render(request, "auth/signin.html", context)

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect("home")
    # return render(request, "auth/signout.html")
    
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True 
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')