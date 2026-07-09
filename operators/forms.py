'''
Form do app operators.
'''

from django import forms

from operators.models import Operator


class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = ['name', 'is_active', 'user']
        labels = {
            'name': 'Nome',
            'is_active': 'Ativo',
            'user': 'Usuário vinculado',
        }
        widgets = {
            'user': forms.Select,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'industrial_input')
        self.fields['name'].widget.attrs['placeholder'] = 'Ex.: João da Silva'
        self.fields['user'].required = False