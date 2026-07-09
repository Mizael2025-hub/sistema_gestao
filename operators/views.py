'''
Views do app operators — CRUD via CBV (RF-C01).

List / Detail / Create / Update / Delete, com login requerido e
permissões por model (operadores: ver; admin: editar).
'''

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from base.view_mixins import PageContextMixin
from operators.forms import OperatorForm
from operators.models import Operator


class OperatorListView(LoginRequiredMixin, PageContextMixin, ListView):
    model = Operator
    template_name = 'operators/operator_list.html'
    context_object_name = 'operators'
    paginate_by = 25

    page_title = 'Operadores'
    page_subtitle = 'Cadastro de operadores de chão de fábrica'
    page_icon = 'users'

    def get_queryset(self):
        qs = Operator.objects.all().order_by('name')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(registration__icontains=q)
        ativo = self.request.GET.get('ativo')
        if ativo in ('1', '0'):
            qs = qs.filter(is_active=bool(int(ativo)))
        return qs


class OperatorDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = Operator
    template_name = 'operators/operator_detail.html'
    context_object_name = 'operator'

    page_title = 'Detalhe do operador'
    page_subtitle = 'Ficha do operador'
    page_icon = 'user'


class OperatorCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    model = Operator
    form_class = OperatorForm
    template_name = 'operators/operator_form.html'
    success_url = reverse_lazy('operators:operator_list')
    permission_required = 'operators.add_operator'

    page_title = 'Novo operador'
    page_subtitle = 'Cadastre um operador'
    page_icon = 'user-plus'


class OperatorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = Operator
    form_class = OperatorForm
    template_name = 'operators/operator_form.html'
    success_url = reverse_lazy('operators:operator_list')
    permission_required = 'operators.change_operator'

    page_title = 'Editar operador'
    page_subtitle = 'Altere os dados do operador'
    page_icon = 'pencil'


class OperatorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
    model = Operator
    template_name = 'operators/operator_confirm_delete.html'
    success_url = reverse_lazy('operators:operator_list')
    permission_required = 'operators.delete_operator'

    page_title = 'Excluir operador'
    page_subtitle = 'Confirme a exclusão'
    page_icon = 'trash-2'