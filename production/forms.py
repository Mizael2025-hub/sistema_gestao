'''
Forms do app production.

- GridProductionForm: validações (turno, máquina/setor coerente) e
  auto-preenchimento do próximo lote (somente leitura).
- GridProductionFilterForm: filtros da listagem (RF-T03).
'''

from django import forms

from catalogs.models import GridModel, Machine, Polarity, Sector, Shift
from operators.models import Operator
from production.models import GridProduction


class GridProductionForm(forms.ModelForm):
    next_lot_preview = forms.CharField(
        label='Próximo lote (auto)',
        required=False,
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
            'production_date': 'Data',
            'operator': 'Operador',
            'machine': 'Máquina',
            'shift': 'Turno',
            'grid_model': 'Modelo',
            'polarity': 'Polaridade',
            'lot': 'Lote',
            'quantity': 'Quantidade',
            'start_time': 'Hora início',
            'end_time': 'Hora fim',
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
        # Lote gerado automaticamente caso vazio.
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