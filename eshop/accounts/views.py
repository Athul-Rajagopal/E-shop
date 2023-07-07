from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from accounts.tokens import account_activation_token

import pyotp
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
import datetime

from eshop import settings


# Create your views here.


# signup

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['pass1']
        password2 = request.POST['pass2']

        if not username.isalnum():
            messages.error(request, 'username must be alpha numeric')
        if password1 != password2:
            messages.error(request, 'password does not match')

        # user object creation
        my_user = User.objects.create_user(username, email, password2)
        my_user.is_active = False
        my_user.save()
        messages.success(request,
                         "Your Account has been Sucessfully created.Please verifiy your email in order to activate your account")

        # senting email to user
        subject = "welcome to eshop-commerce"
        message = "Hello" + ' ' + my_user.username + " !!\n" + "Welcome to eshop \nThank you for visiting website\nwe have also sent you a conforamition email, please confirm your email adress in order to activate your account \n \nThank You"
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        print(send_mail)

        # senting activation link through mail
        current_site = get_current_site(request)
        subject = 'Activate Your Eshop Account'
        message = render_to_string('accounts/confirmEmail.html', {
            'user': my_user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': account_activation_token.make_token(my_user),
        })
        my_user.email_user(subject, message)

        return redirect('signin')
    return render(request, 'accounts/signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass1']

        user = authenticate(username=username, password=password)

        if user is not None:

            # Generate OTP secret
            otp_secret = pyotp.random_base32()

            # Create a PyOTP object
            totp = pyotp.TOTP(otp_secret)

            # Get the current OTP
            otp = totp.now()

            # setting timer
            expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=5)

            # Store OTP in the session
            session = SessionStore(request.session.session_key)
            request.session['otp'] = otp
            request.session['user_id'] = user.id
            request.session['otp_expiration_time'] = expiration_time.timestamp()

            # Compose the email content
            subject = 'OTP verification'
            message = f'Hello {user.username},\n\n' \
                      f'Please use the following OTP to verify your email: {otp}\n\n' \
                      f'Thank you!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            # Send the email
            send_mail(subject, message, from_email, recipient_list)

            return redirect('otplogin')

        else:
            messages.error(request, 'wrong username or password')
            return redirect('signin')

    return render(request, 'accounts/login.html')


# email activation

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None

    if my_user is not None and account_activation_token.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        login(request, my_user)
        return redirect('signin')
    else:
        return render(request, 'accounts/activation_failed.html')


# otp verification
def otp_login(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        # Retrieve OTP from session
        session_otp = request.session.get('otp')
        user_id = request.session.get('user_id')
        expiration_time = request.session.get('otp_expiration_time')

        if session_otp == otp:
            if datetime.datetime.now().timestamp() < expiration_time:

                my_users = User.objects.get(id=user_id)
                login(request, my_users)
                # Clear OTP from session
                request.session['otp'] = None
                request.session['user_id'] = None

                return render(request, 'homepage/home.html', {'user': request.user})

            else:
                # expired otp
                request.session['otp'] = None
                request.session['user_id'] = None
                request.session['otp_expiration_time'] = None
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('otplogin')


        elif request.user.is_authenticated:
            # OTP is invalid, display an error message
            messages.error(request, 'Invalid OTP')

    # OTP verification not completed or authentication failed
    messages.success(request, "We have sent an OTP to your email.")
    return render(request, 'accounts/otpLogin.html')


def home(request):
    return render(request, 'homepage/home.html')


def signout(request):
    logout(request)
    return redirect('home')
