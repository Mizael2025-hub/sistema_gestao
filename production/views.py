'''
Views do app production.

Sprint 3: Teleiras — produção de grade (RF-T01..T04).
Sprint 4: Paradas de máquina (RF-P01..P04).

Fluxo de parada (RF-P01):
1. Localizar a produção por data/operador/máquina (/producao/paradas/localizar/).
2. Selecionar o apontamento → registrar a parada (/producao/paradas/novo/?gp=<id>).
'''

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView,
)

from base.view_mixins import FilteredListMixin, PageContextMixin
from production.forms import (
    GridProductionFilterForm, GridProductionForm,
    GridProductionLocateForm, MachineStopFilterForm, MachineStopForm,
)
from production.models import GridProduction, MachineStop


# --------------------------------------------------------------------- #
# Sprint 3 — Teleiras
# --------------------------------------------------------------------- #
class GridProductionListView(LoginRequiredMixin, FilteredListMixin, PageContextMixin, ListView):
    model = GridProduction
    template_name = 'production/gridproduction_list.html'
    context_object_name = 'grid_productions'
    paginate_by = 25
    filter_form_class = GridProductionFilterForm

    page_title = 'Teleiras — Produção de grade'
    page_subtitle = 'Apontamentos de produção das fundidoras de grade'
    page_icon = 'activity'

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'operator', 'machine', 'machine__sector', 'shift', 'grid_model',
        ).order_by('-production_date', '-start_time')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get('page_obj')
        objs = list(page.object_list) if page else list(ctx.get('grid_productions', []))
        if objs:
            ctx['total_quantity'] = sum(o.quantity for o in objs)
            rates = [o.production_per_hour for o in objs if o.production_per_hour]
            ctx['avg_per_hour'] = round(sum(rates) / len(rates), 2) if rates else 0
        return ctx


class GridProductionDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = GridProduction
    template_name = 'production/gridproduction_detail.html'
    context_object_name = 'gp'

    page_title = 'Detalhe da produção de grade'
    page_subtitle = 'Ficha do apontamento'
    page_icon = 'activity'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['stops'] = self.object.stops.select_related('grid_production').prefetch_related('reasons')
        return ctx


class GridProductionCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    model = GridProduction
    form_class = GridProductionForm
    template_name = 'production/gridproduction_form.html'
    success_url = reverse_lazy('production:gridproduction_list')
    permission_required = 'production.add_gridproduction'

    page_title = 'Novo apontamento — Teleira'
    page_subtitle = 'Registre a produção de grade'
    page_icon = 'activity'


class GridProductionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = GridProduction
    form_class = GridProductionForm
    template_name = 'production/gridproduction_form.html'
    permission_required = 'production.change_gridproduction'

    page_title = 'Editar apontamento — Teleira'
    page_subtitle = 'Altere os dados do apontamento'
    page_icon = 'activity'

    def get_success_url(self):
        return reverse_lazy('production:gridproduction_detail', kwargs={'pk': self.object.pk})


# --------------------------------------------------------------------- #
# Sprint 4 — Paradas de máquina (RF-P01..P04)
# --------------------------------------------------------------------- #
class MachineStopListView(LoginRequiredMixin, FilteredListMixin, PageContextMixin, ListView):
    '''Listagem de paradas com filtros (RF-P04).'''

    model = MachineStop
    template_name = 'production/machinestop_list.html'
    context_object_name = 'stops'
    paginate_by = 25
    filter_form_class = MachineStopFilterForm

    page_title = 'Paradas de máquina'
    page_subtitle = 'Listagem e relatório de paradas das teleiras'
    page_icon = 'shield-alert'

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'grid_production', 'grid_production__operator',
            'grid_production__machine', 'grid_production__grid_model',
        ).prefetch_related('reasons').order_by('-stop_start')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get('page_obj')
        objs = list(page.object_list) if page else list(ctx.get('stops', []))
        if objs:
            ctx['total_stop_hours'] = round(sum(o.duration_hours for o in objs), 2)
            ctx['stops_count'] = len(objs)
        else:
            ctx['total_stop_hours'] = 0
            ctx['stops_count'] = 0
        return ctx


class MachineStopDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = MachineStop
    template_name = 'production/machinestop_detail.html'
    context_object_name = 'stop'

    page_title = 'Detalhe da parada'
    page_subtitle = 'Ficha da parada de máquina'
    page_icon = 'shield-alert'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['gp'] = self.object.grid_production
        return ctx


class MachineStopLocateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, TemplateView):
    '''
    Passo 1 do fluxo RF-P01: localiza a produção por data/operador/máquina.

    Mostra o form de localização e, quando submetido (GET ou POST), lista
    os apontamentos que casam. Cada item leva ao passo 2 (registrar parada).
    '''

    template_name = 'production/machinestop_locate.html'
    permission_required = 'production.add_machinestop'

    page_title = 'Registrar parada — localizar produção'
    page_subtitle = 'Localize o apontamento por data, operador e máquina'
    page_icon = 'search'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = GridProductionLocateForm(self.request.GET or None)
        ctx['locate_form'] = form
        results = []
        if form.is_valid():
            results = form.queryset_results()
        ctx['productions'] = results
        ctx['has_searched'] = form.is_valid() or bool(self.request.GET)
        return ctx


class MachineStopCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    '''
    Passo 2 do fluxo RF-P01: registra a parada vinculada a um apontamento.

    Recebe ?gp=<id_gridproduction>; se ausente, redireciona para a
    localização (passo 1).
    '''

    model = MachineStop
    form_class = MachineStopForm
    template_name = 'production/machinestop_form.html'
    permission_required = 'production.add_machinestop'

    page_title = 'Registrar parada de máquina'
    page_subtitle = 'Informe quando parou, quando voltou e os motivos'
    page_icon = 'shield-alert'

    def dispatch(self, request, *args, **kwargs):
        gp_id = request.GET.get('gp') or request.POST.get('grid_production')
        if not gp_id:
            return redirect('production:machinestop_locate')
        try:
            self.grid_production = GridProduction.objects.get(pk=gp_id)
        except GridProduction.DoesNotExist:
            messages.error(request, 'Apontamento de produção não encontrado.')
            return redirect('production:machinestop_locate')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['gp'] = self.grid_production
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['grid_production'] = self.grid_production
        return kwargs

    def form_valid(self, form):
        stop = form.save(commit=False)
        stop.grid_production = self.grid_production
        stop.save()
        form.save_m2m()
        messages.success(self.request, 'Parada registrada para %s.' % self.grid_production)
        return redirect('production:machinestop_detail', pk=stop.pk)


class MachineStopUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = MachineStop
    form_class = MachineStopForm
    template_name = 'production/machinestop_form.html'
    permission_required = 'production.change_machinestop'

    page_title = 'Editar parada de máquina'
    page_subtitle = 'Altere os dados da parada'
    page_icon = 'shield-alert'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['gp'] = self.object.grid_production
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['grid_production'] = self.object.grid_production
        return kwargs

    def get_success_url(self):
        return reverse_lazy('production:machinestop_detail', kwargs={'pk': self.object.pk})


class MachineStopDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
    model = MachineStop
    template_name = 'production/machinestop_confirm_delete.html'
    permission_required = 'production.delete_machinestop'

    page_title = 'Excluir parada'
    page_subtitle = 'Confirme a exclusão'
    page_icon = 'trash-2'

    def get_success_url(self):
        return reverse_lazy('production:machinestop_list')