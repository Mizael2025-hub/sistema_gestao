'''Forms do app catalogs (cadastros-base).'''

from django import forms

from catalogs.models import (
    Shift, Sector, Machine, GridModel, LeadAlloy, StopReason,
)


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'is_overtime', 'start_time', 'end_time', 'is_active']
        labels = {
            'name': 'Nome', 'is_overtime': 'Hora extra',
            'start_time': 'Hora início', 'end_time': 'Hora fim',
            'is_active': 'Ativo',
        }
        help_texts = {
            'is_overtime': 'Marque para hora extra — os horários ficam opcionais.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['name'].widget.attrs['placeholder'] = 'Ex.: Turno 1 / Hora extra'

    def clean(self):
        cleaned = super().clean()
        is_overtime = cleaned.get('is_overtime')
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if not is_overtime:
            if not start:
                self.add_error('start_time', 'Informe a hora de início (ou marque como hora extra).')
            if not end:
                self.add_error('end_time', 'Informe a hora de fim (ou marque como hora extra).')
            if start and end and end <= start:
                self.add_error('end_time', 'A hora fim deve ser maior que a hora início.')
        return cleaned


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['name', 'is_active']
        labels = {'name': 'Nome', 'is_active': 'Ativo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['name'].widget.attrs['placeholder'] = 'Ex.: Teleiras'


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name', 'sector', 'is_active']
        labels = {'name': 'Nome/Número', 'sector': 'Setor', 'is_active': 'Ativo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['name'].widget.attrs['placeholder'] = 'Ex.: Teleira 1'


class GridModelForm(forms.ModelForm):
    class Meta:
        model = GridModel
        fields = ['name', 'common_name', 'positive_plates', 'negative_plates', 'shares_grid_with', 'is_active']
        labels = {
            'name': 'Nome', 'common_name': 'Nome comum',
            'positive_plates': 'Placas positivas', 'negative_plates': 'Placas negativas',
            'shares_grid_with': 'Compartilha grade com', 'is_active': 'Ativo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['name'].widget.attrs['placeholder'] = 'Ex.: TX5L'
        self.fields['common_name'].widget.attrs['placeholder'] = 'Ex.: ES'
        if self.instance and self.instance.pk:
            self.fields['shares_grid_with'].queryset = GridModel.objects.exclude(pk=self.instance.pk)


class LeadAlloyForm(forms.ModelForm):
    class Meta:
        model = LeadAlloy
        fields = ['code', 'name', 'color', 'is_active']
        labels = {'code': 'Código', 'name': 'Nome', 'color': 'Cor', 'is_active': 'Ativo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')


class StopReasonForm(forms.ModelForm):
    class Meta:
        model = StopReason
        fields = ['code', 'description', 'category', 'is_active']
        labels = {'code': 'Código', 'description': 'Descrição', 'category': 'Categoria', 'is_active': 'Ativo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['code'].widget.attrs['placeholder'] = 'Ex.: MEC-01'
        self.fields['description'].widget.attrs['placeholder'] = 'Ex.: Troca de molde'