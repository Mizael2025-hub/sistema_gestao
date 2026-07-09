'''
Views do app base: login por email, logout e home (dashboard placeholder).
'''

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from base.forms import LoginForm


class LoginView(FormView):
    template_name = 'base/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.redirect_authenticated_user:
            return redirect(LOGIN_REDIRECT := 'base:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # O AuthenticationForm já autenticou via authenticate() em clean(),
        # resolvendo o user_cache de acordo com o backend de email. Basta logar.
        login(self.request, form.get_user())
        return redirect('base:home')


class LogoutAfterPOSTView(TemplateView):
    '''Logout somente via POST (RF de segurança).'''

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

    def get(self, request, *args, **kwargs):
        # Permite logout via link com token CSRF? Não. Redireciona para home.
        return redirect('base:home')


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Dashboard'
        ctx['page_subtitle'] = 'Visão geral'
        ctx['page_icon'] = 'layout-dashboard'
        return ctx