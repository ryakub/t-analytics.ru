from django.urls import path, include
from django.conf.urls import url
from . import views

app_name = 't-auth'

urlpatterns = [
    url(r'^sign-in/$', views.SignIn.as_view(), name='sign-in'),
    # url(r'^sign-out/$', views.LogoutView.as_view(), name='sign-out'),
    url(r'^sign-up/$', views.signup, name='sign-up'),
    url(r'^$', views.start_page, name='start_page'),
    # url(r'^test/$', views.clients_page, name="clients_page"),
    url(r'^connections/$', views.connections, name="connections"),

]