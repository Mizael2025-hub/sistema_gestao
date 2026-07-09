'''
Form de login por email (RF-U02).
'''

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    '''Login por email ao invés de username.'''

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'industrial_input', 'placeholder': 'seu.email@komotors.com'}),
    )
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'industrial_input', 'placeholder': '••••••••'}),
    )

    error_messages = {
        'invalid_login': _('Email ou senha incorretos.'),
        'inactive': _('Esta conta está desativada.'),
    }