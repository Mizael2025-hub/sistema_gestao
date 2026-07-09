'''
Views do app catalogs — CRUD via CBV para cada cadastro-base.

Os setores e ligas são "fixos/seed" — usa as mesmas views para manter
consistência, mas a remoção completa exige permissão de admin.

Compactação: usamos helpers genéricos para evitar 30 views repetidas.
'''

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from base.view_mixins import PageContextMixin
from catalogs.forms import (
    ShiftForm, SectorForm, MachineForm, GridModelForm, LeadAlloyForm, StopReasonForm,
)
from catalogs.models import (
    Shift, Sector, Machine, GridModel, LeadAlloy, StopReason,
)


# --------------------------------------------------------------------- #
# Helper genérico — cria as classes CBV por entidade
# --------------------------------------------------------------------- #
def make_crud(model, form_class, list_title, list_subtitle, list_icon, app_label=None, ordering=None):
    '''Devolve um dict com ListView/DetailView/CreateView/UpdateView/DeleteView.'''
    label = model._meta.model_name
    permission_prefix = '%s.' % (app_label or model._meta.app_label)
    add_perm = '%sadd_%s' % (permission_prefix, label)
    change_perm = '%schange_%s' % (permission_prefix, label)
    delete_perm = '%sdelete_%s' % (permission_prefix, label)
    url_list = 'catalogs:%s_list' % label
    url_detail = 'catalogs:%s_detail' % label
    url_create = 'catalogs:%s_create' % label
    url_update = 'catalogs:%s_update' % label
    url_delete = 'catalogs:%s_delete' % label
    # aliases para evitar self-shadowing no corpo das classes
    _model = model
    _form_class = form_class
    _list_title = list_title
    _list_subtitle = list_subtitle
    _list_icon = list_icon

    class _List(LoginRequiredMixin, PageContextMixin, ListView):
        model = _model
        template_name = 'catalogs/object_list.html'
        context_object_name = 'objects'
        paginate_by = 25
        page_title = _list_title
        page_subtitle = _list_subtitle
        page_icon = _list_icon

        def get_queryset(self):
            qs = model.objects.all()
            if ordering:
                qs = qs.order_by(*ordering)
            else:
                qs = qs.order_by(model._meta.ordering[0] if model._meta.ordering else 'pk')
            q = self.request.GET.get('q')
            if q:
                filt = None
                for f in model._meta.get_fields():
                    name = getattr(f, 'name', None)
                    if name and f.get_internal_type() in ('CharField', 'TextField'):
                        sub = model.objects.filter(** {'%s__icontains' % name: q})
                        filt = sub if filt is None else filt | sub
                if filt is not None:
                    qs = (qs & filt).distinct()
            ativo = self.request.GET.get('ativo')
            if ativo in ('1', '0'):
                qs = qs.filter(is_active=bool(int(ativo)))
            return qs

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['singular'] = model._meta.verbose_name
            ctx['plural'] = model._meta.verbose_name_plural
            ctx['entity_slug'] = label
            ctx['columns'] = _list_columns_for(model)
            ctx['url_list'] = url_list
            ctx['url_detail'] = url_detail
            ctx['url_create'] = url_create
            ctx['url_update'] = url_update
            ctx['url_delete'] = url_delete
            ctx['can_add'] = self.request.user.has_perm(add_perm)
            ctx['can_change'] = self.request.user.has_perm(change_perm)
            ctx['can_delete'] = self.request.user.has_perm(delete_perm)
            return ctx

    class _Detail(LoginRequiredMixin, PageContextMixin, DetailView):
        model = _model
        template_name = 'catalogs/object_detail.html'
        context_object_name = 'object'
        page_title = 'Detalhe · %s' % model._meta.verbose_name
        page_subtitle = ''
        page_icon = _list_icon

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['visible_fields'] = _detail_fields_for(model)
            ctx['singular'] = model._meta.verbose_name
            ctx['entity_slug'] = label
            ctx['url_list'] = url_list
            ctx['url_update'] = url_update
            ctx['url_delete'] = url_delete
            ctx['can_change'] = self.request.user.has_perm(change_perm)
            ctx['can_delete'] = self.request.user.has_perm(delete_perm)
            return ctx

    class _Create(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
        model = _model
        form_class = _form_class
        template_name = 'catalogs/object_form.html'
        permission_required = '%sadd_%s' % (permission_prefix, label)
        page_title = 'Novo · %s' % model._meta.verbose_name
        page_subtitle = 'Cadastre um registro'
        page_icon = _list_icon

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['singular'] = model._meta.verbose_name
            ctx['entity_slug'] = label
            ctx['url_list'] = url_list
            return ctx

        def get_success_url(self):
            return reverse_lazy('catalogs:%s_list' % label)

    class _Update(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
        model = _model
        form_class = _form_class
        template_name = 'catalogs/object_form.html'
        permission_required = '%schange_%s' % (permission_prefix, label)
        page_title = 'Editar · %s' % model._meta.verbose_name
        page_subtitle = ''
        page_icon = _list_icon

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['singular'] = model._meta.verbose_name
            ctx['entity_slug'] = label
            ctx['url_list'] = url_list
            return ctx

        def get_success_url(self):
            return reverse_lazy('catalogs:%s_list' % label)

    class _Delete(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
        model = _model
        template_name = 'catalogs/object_confirm_delete.html'
        permission_required = '%sdelete_%s' % (permission_prefix, label)
        page_title = 'Excluir · %s' % model._meta.verbose_name
        page_subtitle = ''
        page_icon = 'trash-2'

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx['singular'] = model._meta.verbose_name
            ctx['plural'] = model._meta.verbose_name_plural
            ctx['entity_slug'] = label
            ctx['url_list'] = url_list
            return ctx

        def get_success_url(self):
            return reverse_lazy('catalogs:%s_list' % label)

    return {'list': _List, 'detail': _Detail, 'create': _Create, 'update': _Update, 'delete': _Delete}


def _list_columns_for(model):
    '''Lista de (name, label) para colunas da listagem.'''
    skip = {'id', 'created_at', 'updated_at', 'shares_grid_with'}
    cols = []
    for f in model._meta.get_fields():
        name = getattr(f, 'name', None)
        if not name or name in skip:
            continue
        if f.is_relation and not f.many_to_one:
            continue
        label = getattr(f, 'verbose_name', None) or name
        cols.append((name, str(label).capitalize()))
    return cols


def _detail_fields_for(model):
    skip = {'id'}
    fields = []
    for f in model._meta.get_fields():
        name = getattr(f, 'name', None)
        if not name or name in skip:
            continue
        if f.is_relation and not f.many_to_one:
            continue
        if f.many_to_one or f.one_to_one:
            fields.append((name, True))
        else:
            fields.append((name, False))
    return fields


# --------------------------------------------------------------------- #
# Geração das views por entidade
# --------------------------------------------------------------------- #
shift_crud = make_crud(Shift, ShiftForm, 'Turnos', 'Cadastro de turnos', 'clock', ordering=('start_time',))
sector_crud = make_crud(Sector, SectorForm, 'Setores', 'Cadastro de setores', 'building-2', ordering=('name',))
machine_crud = make_crud(Machine, MachineForm, 'Máquinas', 'Cadastro de máquinas/teleiras', 'cpu', ordering=('name',))
gridmodel_crud = make_crud(GridModel, GridModelForm, 'Modelos', 'Cadastro de modelos de grade', 'battery-charging', ordering=('name',))
leadalloy_crud = make_crud(LeadAlloy, LeadAlloyForm, 'Ligas', 'Cadastro de ligas de chumbo', 'droplet', ordering=('code',))
stopreason_crud = make_crud(StopReason, StopReasonForm, 'Motivos de parada', 'Cadastro de motivos de parada', 'shield-alert', ordering=('category', 'description'))


# Exposição das classes (usadas em urls.py)
ShiftListView = shift_crud['list']
ShiftDetailView = shift_crud['detail']
ShiftCreateView = shift_crud['create']
ShiftUpdateView = shift_crud['update']
ShiftDeleteView = shift_crud['delete']

SectorListView = sector_crud['list']
SectorDetailView = sector_crud['detail']
SectorCreateView = sector_crud['create']
SectorUpdateView = sector_crud['update']
SectorDeleteView = sector_crud['delete']

MachineListView = machine_crud['list']
MachineDetailView = machine_crud['detail']
MachineCreateView = machine_crud['create']
MachineUpdateView = machine_crud['update']
MachineDeleteView = machine_crud['delete']

GridModelListView = gridmodel_crud['list']
GridModelDetailView = gridmodel_crud['detail']
GridModelCreateView = gridmodel_crud['create']
GridModelUpdateView = gridmodel_crud['update']
GridModelDeleteView = gridmodel_crud['delete']

LeadAlloyListView = leadalloy_crud['list']
LeadAlloyDetailView = leadalloy_crud['detail']
LeadAlloyCreateView = leadalloy_crud['create']
LeadAlloyUpdateView = leadalloy_crud['update']
LeadAlloyDeleteView = leadalloy_crud['delete']

StopReasonListView = stopreason_crud['list']
StopReasonDetailView = stopreason_crud['detail']
StopReasonCreateView = stopreason_crud['create']
StopReasonUpdateView = stopreason_crud['update']
StopReasonDeleteView = stopreason_crud['delete']