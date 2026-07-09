'''URLs do app base.'''

from django.urls import path

from base import views

app_name = 'base'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]