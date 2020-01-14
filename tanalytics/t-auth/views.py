from django.shortcuts import render
from django.http import HttpResponse
from .forms import SignInForm, SignUpForm
from django.contrib.auth import authenticate, login
from django.views import View
from django.contrib.auth.views import LogoutView
# Create your views here.


class SignIn(View):
   def post(self, request):
       form = SignInForm(request.POST)
       if form.is_valid():
           cd = form.cleaned_data
           user = authenticate(
               request,
               username=cd['login'],
               password=cd['password']
           )
           if user is None:
               return HttpResponse("Неправильный логин и/или пароль")
           if not user.is_active:
               return HttpResponse("Ваш аккаунт заблокирован")
           login(request, user)
           return HttpResponse("Добро пожаловать! Успешный вход!")
       return render(request, 't-auth/sign-in.html', {"form": form})

   def get(self, request):
       form = SignInForm()
       return render(request, 't-auth/sign-in.html', {"form": form})


def start_page(request):
    return HttpResponse("Hello from start page!")


def signin(request):
    form = SignInForm()
    return render(request, 't-auth/sign-in.html', {"form": form})


def signup(request):
    form = SignUpForm()
    return render(request, 't-auth/sign-up.html', {"form": form})


def clients_page(request):
    return render(request, 't-auth/page-clients.html')


def connections(request):
    return render(request, 't-auth/connections.html')


def base2(request):
    return render(request, 't-auth/base2.html')
