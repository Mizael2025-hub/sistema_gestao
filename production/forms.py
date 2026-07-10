'''
Forms do app production.

Sprint 3:
- GridProductionForm: validações e auto-preenchimento do lote.
- GridProductionFilterForm: filtros da listagem (RF-T03).

Sprint 4:
- GridProductionLocateForm: localiza produção por data/operador/máquina
  antes de registrar parada (RF-P01).
- MachineStopForm: registra/edita a parada (hora que parou/voltou + motivos).
- MachineStopFilterForm: filtros da listagem de paradas (RF-P04).
'''

from django import forms

from catalogs.models import GridModel, Machine, Polarity, Shift, StopReason
from operators.models import Operator
from production.models import GridProduction, MachineStop, PasteProduction


class GridProductionForm(forms.ModelForm):
    next_lot_preview = forms.CharField(
        label='Próximo lote (auto)', required=False,
        help_text='Lote gerado automaticamente ao salvar.',
    )

    class Meta:
        model = GridProduction
        fields = [
            'production_date', 'operator', 'machine', 'shift',
            'grid_model', 'polarity', 'lot', 'quantity',
            'start_time', 'end_time',
        ]
        labels = {
            'production_date': 'Data', 'operator': 'Operador',
            'machine': 'Máquina', 'shift': 'Turno',
            'grid_model': 'Modelo', 'polarity': 'Polaridade',
            'lot': 'Lote', 'quantity': 'Quantidade',
            'start_time': 'Hora início', 'end_time': 'Hora fim',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['next_lot_preview'].widget.attrs['readonly'] = True
        self.fields['next_lot_preview'].widget.attrs['value'] = GridProduction.next_lot()
        self.fields['lot'].required = False
        self.fields['lot'].widget = forms.HiddenInput()
        self.fields['lot'].widget.attrs['value'] = GridProduction.next_lot()
        self.fields['start_time'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local', 'class': 'industrial_input',
        })
        self.fields['end_time'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local', 'class': 'industrial_input',
        })
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_end_time(self):
        start = self.cleaned_data.get('start_time')
        end = self.cleaned_data.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('Hora fim deve ser posterior à hora início.')
        return end

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.lot:
            instance.lot = GridProduction.next_lot()
        if commit:
            instance.save()
        return instance


class GridProductionFilterForm(forms.Form):
    production_date = forms.DateField(label='Data', required=False)
    operator = forms.ModelChoiceField(queryset=Operator.objects.all(), label='Operador', required=False)
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), label='Máquina', required=False)
    shift = forms.ModelChoiceField(queryset=Shift.objects.all(), label='Turno', required=False)
    grid_model = forms.ModelChoiceField(queryset=GridModel.objects.all(), label='Modelo', required=False)
    polarity = forms.ChoiceField(
        choices=[('', '------')] + Polarity.choices, label='Polaridade', required=False,
    )
    lot = forms.CharField(label='Lote', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['production_date'].widget = forms.DateInput(attrs={
            'type': 'date', 'class': 'industrial_input',
        })

    def filter_queryset(self, qs):
        cd = self.cleaned_data
        if not cd:
            return qs
        if cd.get('production_date'):
            qs = qs.filter(production_date__exact=cd['production_date'])
        for field in ('operator', 'machine', 'shift', 'grid_model', 'polarity'):
            val = cd.get(field)
            if val:
                qs = qs.filter(**{field: val})
        lot = cd.get('lot', '').strip()
        if lot:
            qs = qs.filter(lot__icontains=lot)
        return qs


# --------------------------------------------------------------------- #
# Sprint 4 — Paradas de máquina (RF-P01..P04)
# --------------------------------------------------------------------- #
class GridProductionLocateForm(forms.Form):
    '''
    Localiza o registro de produção por data, operador e máquina (RF-P01).

    Todos os campos são opcionais — a busca aplica apenas os critérios
    preenchidos, permitindo filtrar por qualquer combinação (ex.: só data,
    só operador, data+operador, etc.).
    '''

    production_date = forms.DateField(label='Data', required=False)
    operator = forms.ModelChoiceField(
        queryset=Operator.objects.all(), label='Operador', required=False,
    )
    machine = forms.ModelChoiceField(
        queryset=Machine.objects.all(), label='Máquina', required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['production_date'].widget = forms.DateInput(attrs={
            'type': 'date', 'class': 'industrial_input',
        })

    def queryset_results(self):
        '''Retorna os GridProduction que casam com os critérios informados.'''
        if not self.is_valid():
            return GridProduction.objects.none()
        cd = self.cleaned_data
        qs = GridProduction.objects.all()
        if cd.get('production_date'):
            qs = qs.filter(production_date=cd['production_date'])
        if cd.get('operator'):
            qs = qs.filter(operator=cd['operator'])
        if cd.get('machine'):
            qs = qs.filter(machine=cd['machine'])
        return qs.select_related(
            'operator', 'machine', 'shift', 'grid_model',
        ).order_by('-production_date', '-start_time')


class MachineStopForm(forms.ModelForm):
    '''
    Registra/edita uma parada de máquina (RF-P01/P02).
    O grid_production é informado pela view (preenchido automaticamente
    após a localização).
    '''

    class Meta:
        model = MachineStop
        fields = ['stop_start', 'stop_end', 'reasons', 'note']
        labels = {
            'stop_start': 'Hora que parou',
            'stop_end': 'Hora que voltou',
            'reasons': 'Motivo(s)',
            'note': 'Observação',
        }
        help_texts = {
            'reasons': 'Selecione um ou mais motivos (RF-P02).',
            'note': 'Opcional.',
        }

    def __init__(self, *args, grid_production=None, **kwargs):
        self.grid_production = grid_production
        super().__init__(*args, **kwargs)
        # Define o grid_production na instância antes da validação (_post_clean
        # chama instance.full_clean, que invoca MachineStop.clean()).
        if self.grid_production is not None and self.instance is not None:
            self.instance.grid_production = self.grid_production
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['stop_start'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'industrial_input'},
            format='%Y-%m-%dT%H:%M',
        )
        self.fields['stop_end'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'industrial_input'},
            format='%Y-%m-%dT%H:%M',
        )
        self.fields['stop_start'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['stop_end'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['reasons'].queryset = StopReason.objects.filter(is_active=True)
        self.fields['reasons'].widget.attrs.setdefault('class', 'industrial_input')
        self.fields['reasons'].widget.attrs.setdefault('size', '6')
        self.fields['note'].widget = forms.Textarea(attrs={
            'class': 'industrial_input', 'rows': '3',
        })

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('stop_start')
        end = cleaned.get('stop_end')
        if start and end and end <= start:
            self.add_error('stop_end', 'A hora que voltou deve ser maior que a hora que parou.')
        gp = self.grid_production or (self.instance.grid_production if self.instance else None)
        if gp and gp.start_time and gp.end_time:
            if start and start < gp.start_time:
                self.add_error('stop_start', 'A parada não pode iniciar antes do apontamento (%s).' % gp.start_time.strftime('%d/%m/%Y %H:%M'))
            if end and end > gp.end_time:
                self.add_error('stop_end', 'A parada não pode terminar depois do apontamento (%s).' % gp.end_time.strftime('%d/%m/%Y %H:%M'))
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.grid_production is not None:
            instance.grid_production = self.grid_production
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class MachineStopFilterForm(forms.Form):
    '''Filtros da listagem de paradas (RF-P04).'''

    stop_date = forms.DateField(label='Data da parada', required=False)
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), label='Máquina', required=False)
    operator = forms.ModelChoiceField(queryset=Operator.objects.all(), label='Operador', required=False)
    reason = forms.ModelChoiceField(queryset=StopReason.objects.all(), label='Motivo', required=False)
    grid_model = forms.ModelChoiceField(queryset=GridModel.objects.all(), label='Modelo', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['stop_date'].widget = forms.DateInput(attrs={
            'type': 'date', 'class': 'industrial_input',
        })

    def filter_queryset(self, qs):
        cd = self.cleaned_data
        if not cd:
            return qs
        if cd.get('stop_date'):
            qs = qs.filter(stop_start__date=cd['stop_date'])
        if cd.get('machine'):
            qs = qs.filter(grid_production__machine=cd['machine'])
        if cd.get('operator'):
            qs = qs.filter(grid_production__operator=cd['operator'])
        if cd.get('reason'):
            qs = qs.filter(reasons=cd['reason'])
        if cd.get('grid_model'):
            qs = qs.filter(grid_production__grid_model=cd['grid_model'])
        return qs.distinct()


# --------------------------------------------------------------------- #
# Sprint 5 — Empaste e consumos (RF-E01..E04)
# --------------------------------------------------------------------- #
class PasteProductionForm(forms.ModelForm):
    '''
    Registra/edita um empaste (RF-E01).

    O lote é gerado automaticamente a partir da data (`EP{DDMMYYYY}`) e
    NÃO é editável manualmente (RF-E02) — exibido como readonly.

    O widget de data usa `type=date` com format ISO (YYYY-MM-DD) para que o
    navegador exiba corretamente o valor ao editar (input type=date exige
    ISO); o envio é convertido por Django via DATE_INPUT_FORMATS.
    '''

    class Meta:
        model = PasteProduction
        fields = ['paste_date', 'grid_model', 'polarity', 'pasted_quantity', 'panel_loss', 'grid_loss']
        labels = {
            'paste_date': 'Data',
            'grid_model': 'Modelo',
            'polarity': 'Polaridade',
            'pasted_quantity': 'Quantidade empastada',
            'panel_loss': 'Perda em painel',
            'grid_loss': 'Perda de grade',
        }
        help_texts = {
            'panel_loss': 'Painéis perdidos (opcional).',
            'grid_loss': 'Grades perdidas (opcional).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        # type=date exige valor no formato ISO (YYYY-MM-DD); sem format
        # explícito o Django renderizaria no formato do locale (dd/mm/aaaa)
        # e o navegador exibiria o campo em branco ao editar.
        self.fields['paste_date'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'industrial_input'},
            format='%Y-%m-%d',
        )
        self.fields['paste_date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('paste_date'):
            raise forms.ValidationError({'paste_date': 'Informe a data do empaste.'})
        return cleaned


class PasteProductionFilterForm(forms.Form):
    '''Filtros da listagem de empastes (RF-E04).'''

    paste_date = forms.DateField(label='Data', required=False)
    grid_model = forms.ModelChoiceField(queryset=GridModel.objects.all(), label='Modelo', required=False)
    polarity = forms.ChoiceField(
        choices=[('', '------')] + Polarity.choices, label='Polaridade', required=False,
    )
    lot = forms.CharField(label='Lote', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['paste_date'].widget = forms.DateInput(attrs={
            'type': 'date', 'class': 'industrial_input',
        })

    def filter_queryset(self, qs):
        cd = self.cleaned_data
        if not cd:
            return qs
        if cd.get('paste_date'):
            qs = qs.filter(paste_date__exact=cd['paste_date'])
        if cd.get('grid_model'):
            qs = qs.filter(grid_model=cd['grid_model'])
        if cd.get('polarity'):
            qs = qs.filter(polarity=cd['polarity'])
        lot = cd.get('lot', '').strip()
        if lot:
            qs = qs.filter(lot__icontains=lot)
        return qs