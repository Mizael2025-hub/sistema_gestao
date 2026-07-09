'''
URL configuration for core project.

Healthcheck sem DB e sem auth; telas de auth (login/logout) por email;
admin do Django; includes dos apps de domínio.
'''

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

from base.views import LoginView, LogoutAfterPOSTView


def health(request):
    '''Healthcheck leve: 200 sem DB e sem auth.'''
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),

    # Auth por email (RF-U02)
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutAfterPOSTView.as_view(), name='logout'),

    # Apps de domínio
    path('', include('base.urls')),
    path('operadores/', include('operators.urls')),
    path('cadastros/', include('catalogs.urls')),
    path('producao/', include('production.urls')),
]