from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login', views.otp_login, name='otplogin'),
    path('home', views.home, name='home'),
    path('signout', views.signout, name='signout'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
    path('otp-forgot-password', views.otp_forgot_password, name='otp_forgot_password'),
    path('reset-password', views.reset_password, name='reset_password')
]
