'''
Views do app production.

Sprint 3: Teleiras — produção de grade (RF-T01..T04).
Sprint 4: Paradas de máquina (RF-P01..P04).
Sprint 5: Empaste e consumos (RF-E01..E04).
Sprint 6: Masseira, Montagem, Formação (RF-M01, RF-MO01, RF-F01..F02).

Fluxo de parada (RF-P01):
1. Localizar a produção por data/operador/máquina (/producao/paradas/localizar/).
2. Selecionar o apontamento → registrar a parada (/producao/paradas/novo/?gp=<id>).
'''

import csv
import io
from datetime import datetime as _datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView,
)

from base.view_mixins import FilteredListMixin, PageContextMixin
from production.forms import (
    AssemblyFilterForm, AssemblyForm,
    FormationFilterForm, FormationForm, FormationImportForm,
    GridProductionFilterForm, GridProductionForm,
    GridProductionLocateForm, MachineStopFilterForm, MachineStopForm,
    MassProductionFilterForm, MassProductionForm,
    PasteProductionFilterForm, PasteProductionForm,
)
from production.models import (
    Assembly, Formation, GridProduction, MachineStop, MassProduction, PasteProduction,
)
from catalogs.models import GridModel  # utilizado pela importação de Formação (RF-F02)


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


# --------------------------------------------------------------------- #
# Sprint 5 — Empaste e consumos (RF-E01..E04)
# --------------------------------------------------------------------- #
class PasteProductionListView(LoginRequiredMixin, FilteredListMixin, PageContextMixin, ListView):
    '''Listagem de empastes com filtros (RF-E04).'''

    model = PasteProduction
    template_name = 'production/pasteproduction_list.html'
    context_object_name = 'pastes'
    paginate_by = 25
    filter_form_class = PasteProductionFilterForm

    page_title = 'Empaste'
    page_subtitle = 'Apontamentos da empastadeira'
    page_icon = 'layers'

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'grid_model', 'oxide_consumption',
        ).order_by('-paste_date', '-id')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get('page_obj')
        objs = list(page.object_list) if page else list(ctx.get('pastes', []))
        if objs:
            ctx['total_pasted'] = sum(o.pasted_quantity for o in objs)
            ctx['total_panel_loss'] = sum(o.panel_loss for o in objs)
            ctx['total_grid_loss'] = sum(o.grid_loss for o in objs)
        else:
            ctx['total_pasted'] = 0
            ctx['total_panel_loss'] = 0
            ctx['total_grid_loss'] = 0
        return ctx


class PasteProductionDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = PasteProduction
    template_name = 'production/pasteproduction_detail.html'
    context_object_name = 'paste'

    page_title = 'Detalhe do empaste'
    page_subtitle = 'Ficha do empaste'
    page_icon = 'layers'


class PasteProductionCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    model = PasteProduction
    form_class = PasteProductionForm
    template_name = 'production/pasteproduction_form.html'
    success_url = reverse_lazy('production:pasteproduction_list')
    permission_required = 'production.add_pasteproduction'

    page_title = 'Novo empaste'
    page_subtitle = 'Registre o empaste da empastadeira'
    page_icon = 'layers'


class PasteProductionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = PasteProduction
    form_class = PasteProductionForm
    template_name = 'production/pasteproduction_form.html'
    permission_required = 'production.change_pasteproduction'

    page_title = 'Editar empaste'
    page_subtitle = 'Altere os dados do empaste'
    page_icon = 'layers'

    def get_success_url(self):
        return reverse_lazy('production:pasteproduction_detail', kwargs={'pk': self.object.pk})


class PasteProductionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
    model = PasteProduction
    template_name = 'production/pasteproduction_confirm_delete.html'
    permission_required = 'production.delete_pasteproduction'

    page_title = 'Excluir empaste'
    page_subtitle = 'Confirme a exclusão'
    page_icon = 'trash-2'

    def get_success_url(self):
        return reverse_lazy('production:pasteproduction_list')


# --------------------------------------------------------------------- #
# Sprint 6 — Masseira, Montagem, Formação (RF-M01, RF-MO01, RF-F01..F02)
# --------------------------------------------------------------------- #
# ---- Masseira (RF-M01) ---------------------------------------------- #
class MassProductionListView(LoginRequiredMixin, FilteredListMixin, PageContextMixin, ListView):
    model = MassProduction
    template_name = 'production/massproduction_list.html'
    context_object_name = 'masses'
    paginate_by = 25
    filter_form_class = MassProductionFilterForm

    page_title = 'Masseira'
    page_subtitle = 'Apontamentos da masseira'
    page_icon = 'flask-conical'

    def get_queryset(self):
        return super().get_queryset().order_by('-mass_date', '-id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get('page_obj')
        objs = list(page.object_list) if page else list(ctx.get('masses', []))
        if objs:
            ctx['total_weight'] = sum(o.weight for o in objs)
        else:
            ctx['total_weight'] = 0
        return ctx


class MassProductionDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = MassProduction
    template_name = 'production/massproduction_detail.html'
    context_object_name = 'mass'

    page_title = 'Detalhe da masseira'
    page_subtitle = 'Ficha do apontamento'
    page_icon = 'flask-conical'


class MassProductionCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    model = MassProduction
    form_class = MassProductionForm
    template_name = 'production/massproduction_form.html'
    success_url = reverse_lazy('production:massproduction_list')
    permission_required = 'production.add_massproduction'

    page_title = 'Nova masseira'
    page_subtitle = 'Registre o apontamento da masseira'
    page_icon = 'flask-conical'


class MassProductionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = MassProduction
    form_class = MassProductionForm
    template_name = 'production/massproduction_form.html'
    permission_required = 'production.change_massproduction'

    page_title = 'Editar masseira'
    page_subtitle = 'Altere os dados do apontamento'
    page_icon = 'flask-conical'

    def get_success_url(self):
        return reverse_lazy('production:massproduction_detail', kwargs={'pk': self.object.pk})


class MassProductionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
    model = MassProduction
    template_name = 'production/massproduction_confirm_delete.html'
    permission_required = 'production.delete_massproduction'

    page_title = 'Excluir masseira'
    page_subtitle = 'Confirme a exclusão'
    page_icon = 'trash-2'

    def get_success_url(self):
        return reverse_lazy('production:massproduction_list')


# ---- Montagem (RF-MO01) --------------------------------------------- #
class AssemblyListView(LoginRequiredMixin, FilteredListMixin, PageContextMixin, ListView):
    model = Assembly
    template_name = 'production/assembly_list.html'
    context_object_name = 'assemblies'
    paginate_by = 25
    filter_form_class = AssemblyFilterForm

    page_title = 'Montagem'
    page_subtitle = 'Apontamentos de montagem'
    page_icon = 'package'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'grid_model', 'positive_ep', 'negative_ep',
        ).order_by('-assembly_date', '-id')


class AssemblyDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = Assembly
    template_name = 'production/assembly_detail.html'
    context_object_name = 'assembly'

    page_title = 'Detalhe da montagem'
    page_subtitle = 'Ficha do apontamento'
    page_icon = 'package'


class AssemblyCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    model = Assembly
    form_class = AssemblyForm
    template_name = 'production/assembly_form.html'
    success_url = reverse_lazy('production:assembly_list')
    permission_required = 'production.add_assembly'

    page_title = 'Nova montagem'
    page_subtitle = 'Registre a montagem'
    page_icon = 'package'


class AssemblyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = Assembly
    form_class = AssemblyForm
    template_name = 'production/assembly_form.html'
    permission_required = 'production.change_assembly'

    page_title = 'Editar montagem'
    page_subtitle = 'Altere os dados da montagem'
    page_icon = 'package'

    def get_success_url(self):
        return reverse_lazy('production:assembly_detail', kwargs={'pk': self.object.pk})


class AssemblyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
    model = Assembly
    template_name = 'production/assembly_confirm_delete.html'
    permission_required = 'production.delete_assembly'

    page_title = 'Excluir montagem'
    page_subtitle = 'Confirme a exclusão'
    page_icon = 'trash-2'

    def get_success_url(self):
        return reverse_lazy('production:assembly_list')


# ---- Formação (RF-F01..F02) ----------------------------------------- #
class FormationListView(LoginRequiredMixin, FilteredListMixin, PageContextMixin, ListView):
    model = Formation
    template_name = 'production/formation_list.html'
    context_object_name = 'formations'
    paginate_by = 25
    filter_form_class = FormationFilterForm

    page_title = 'Formação'
    page_subtitle = 'Apontamentos de formação'
    page_icon = 'battery-charging'

    def get_queryset(self):
        return super().get_queryset().select_related('grid_model').order_by('-formation_date', '-table_number')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = ctx.get('page_obj')
        objs = list(page.object_list) if page else list(ctx.get('formations', []))
        ctx['total_quantity'] = sum(o.quantity for o in objs) if objs else 0
        return ctx


class FormationDetailView(LoginRequiredMixin, PageContextMixin, DetailView):
    model = Formation
    template_name = 'production/formation_detail.html'
    context_object_name = 'formation'

    page_title = 'Detalhe da formação'
    page_subtitle = 'Ficha do apontamento'
    page_icon = 'battery-charging'


class FormationCreateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, CreateView):
    model = Formation
    form_class = FormationForm
    template_name = 'production/formation_form.html'
    success_url = reverse_lazy('production:formation_list')
    permission_required = 'production.add_formation'

    page_title = 'Nova formação'
    page_subtitle = 'Registre a formação'
    page_icon = 'battery-charging'


class FormationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, UpdateView):
    model = Formation
    form_class = FormationForm
    template_name = 'production/formation_form.html'
    permission_required = 'production.change_formation'

    page_title = 'Editar formação'
    page_subtitle = 'Altere os dados da formação'
    page_icon = 'battery-charging'

    def get_success_url(self):
        return reverse_lazy('production:formation_detail', kwargs={'pk': self.object.pk})


class FormationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, DeleteView):
    model = Formation
    template_name = 'production/formation_confirm_delete.html'
    permission_required = 'production.delete_formation'

    page_title = 'Excluir formação'
    page_subtitle = 'Confirme a exclusão'
    page_icon = 'trash-2'

    def get_success_url(self):
        return reverse_lazy('production:formation_list')


class FormationImportView(LoginRequiredMixin, PermissionRequiredMixin, PageContextMixin, FormView):
    '''
    Importação por planilha (CSV) para Formação — RF-F02.

    Parser seguro: detecta delimitador, valida linha a linha, cria em lote
    dentro de transação atômica e reporta erros por linha (sem abortar tudo).
    '''

    form_class = FormationImportForm
    template_name = 'production/formation_import.html'
    permission_required = 'production.add_formation'
    success_url = reverse_lazy('production:formation_list')

    page_title = 'Importar formações (planilha)'
    page_subtitle = 'Importe registros de formação a partir de um CSV'
    page_icon = 'upload'

    # Mapeamento de cabeçalhos aceitos (sinônimos minúsculos sem acento).
    HEADER_ALIASES = {
        'data': 'formation_date',
        'data_formacao': 'formation_date',
        'mesa': 'table_number',
        'numero_mesa': 'table_number',
        'lote': 'battery_lot',
        'lote_bateria': 'battery_lot',
        'modelo': 'grid_model',
        'modelo_bateria': 'grid_model',
        'quantidade': 'quantity',
        'qtd': 'quantity',
    }

    def form_valid(self, form):
        uploaded = form.cleaned_data['file']
        decoded = uploaded.read().decode('utf-8-sig', errors='replace')
        reader = self._build_reader(decoded)
        rows = list(reader)
        if not rows:
            messages.error(self.request, 'Arquivo vazio.')
            return self.form_invalid(form)

        header = [self._norm(h) for h in rows[0]]
        colmap = self._map_headers(header)
        missing = {'formation_date', 'table_number', 'battery_lot', 'grid_model', 'quantity'} - set(colmap.values())
        if missing:
            messages.error(
                self.request,
                'Cabeçalhos insuficientes. Faltam colunas: %s. '
                'Esperado: data, mesa, lote, modelo, quantidade.' % ', '.join(sorted(missing)),
            )
            return self.form_invalid(form)

        models_index = {gm.name.upper(): gm for gm in GridModel.objects.all()}
        created, errors = 0, []
        with transaction.atomic():
            for i, row in enumerate(rows[1:], start=2):
                try:
                    rec = self._row_to_record(row, header, colmap, models_index)
                except _ImportRowError as exc:
                    errors.append('Linha %d: %s' % (i, exc))
                    continue
                try:
                    rec.full_clean()
                    rec.save()
                    created += 1
                except ValidationError as exc:
                    errors.append('Linha %d: %s' % (i, '; '.join(exc.messages)))

        if created:
            messages.success(self.request, 'Importação concluída: %d registro(s) criado(s).' % created)
        if errors:
            preview = errors[:20]
            more = '' if len(errors) <= 20 else ' (mais %d linha(s) com erro)' % (len(errors) - 20)
            messages.error(
                self.request,
                '%d linha(s) ignorada(s):%s\n%s' % (len(errors), more, '\n'.join(preview)),
            )
        if not created and not errors:
            messages.warning(self.request, 'Nenhuma linha de dados encontrada.')
        return super().form_valid(form)

    # ---- Helpers do parser seguro -------------------------------------
    @staticmethod
    def _norm(text):
        import unicodedata
        s = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode('ascii')
        return s.strip().lower().replace(' ', '_')

    @staticmethod
    def _build_reader(text):
        sample = text.splitlines()[:5]
        try:
            dialect = csv.Sniffer().sniff('\n'.join(sample), delimiters=',;\t|')
        except csv.Error:
            dialect = csv.excel
        return csv.reader(io.StringIO(text), dialect)

    def _map_headers(self, header):
        colmap = {}
        for idx, h in enumerate(header):
            field = self.HEADER_ALIASES.get(h)
            if field:
                colmap[idx] = field
        return colmap

    @staticmethod
    def _row_to_record(row, header, colmap, models_index):
        data = {}
        for idx, field in colmap.items():
            if idx < len(row):
                data[field] = (row[idx] or '').strip()
        if not any(data.values()):
            raise _ImportRowError('linha vazia')
        # data
        raw_date = data.get('formation_date', '')
        formation_date = FormationImportView._parse_date(raw_date)
        if not formation_date:
            raise _ImportRowError('data inválida "%s"' % raw_date)
        # mesa
        try:
            table_number = int(str(data.get('table_number', '')).replace('.', '').replace(',', ''))
        except ValueError:
            raise _ImportRowError('número da mesa inválido "%s"' % data.get('table_number'))
        if table_number <= 0:
            raise _ImportRowError('número da mesa deve ser positivo')
        # lote
        battery_lot = data.get('battery_lot', '')
        if not battery_lot:
            raise _ImportRowError('lote da bateria vazio')
        # modelo
        gm = models_index.get(str(data.get('grid_model', '')).strip().upper())
        if gm is None:
            raise _ImportRowError('modelo "%s" não cadastrado' % data.get('grid_model'))
        # quantidade
        try:
            quantity = int(str(data.get('quantity', '')).replace('.', '').replace(',', ''))
        except ValueError:
            raise _ImportRowError('quantidade inválida "%s"' % data.get('quantity'))
        if quantity <= 0:
            raise _ImportRowError('quantidade deve ser positiva')
        return Formation(
            formation_date=formation_date, table_number=table_number,
            battery_lot=battery_lot, grid_model=gm, quantity=quantity,
        )

    @staticmethod
    def _parse_date(value):
        value = (value or '').strip()
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
            try:
                return _datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None


class _ImportRowError(Exception):
    '''Erro de uma linha específica durante importação (não aborta o lote).'''
    pass