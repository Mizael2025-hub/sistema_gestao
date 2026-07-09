'''
Views do app production — Sprint 3: Teleiras (RF-T01..T04).

List / Detail / Create / Update via CBV, com filtros, paginação e
permissões por usuário (RF-T03), aderentes ao design system.
'''

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from base.view_mixins import FilteredListMixin, PageContextMixin
from production.forms import GridProductionFilterForm, GridProductionForm
from production.models import GridProduction


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