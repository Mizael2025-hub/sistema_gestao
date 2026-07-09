'''
Filtros de template do app base.

- add_class: adiciona classe CSS a um BoundField (widget).
- placeholder: aplica placeholder ao widget.
- cell_value: renderiza o valor de um campo de model em template genérico
  (lida com FKs, choices, datas e booleans) de forma pt-BR amigável.
'''

from django import template
from django.forms import BoundField
from django.utils.formats import date_format
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={**(field.field.widget.attrs or {}), 'class': css_class})
    return field


@register.filter(name='placeholder')
def placeholder(field, text):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={**(field.field.widget.attrs or {}), 'placeholder': text})
    return field


@register.simple_tag
def cell_value(obj, field_name):
    '''Renderiza amigavelmente o valor de um atributo de um model.'''
    value = getattr(obj, field_name, None)
    if value is None:
        return mark_safe('<span style="color:var(--apple_text_secondary)">—</span>')

    # Choices (CharField com choices): exibe display
    fld = None
    try:
        fld = obj._meta.get_field(field_name)
    except Exception:
        fld = None
    if fld is not None and fld.get_internal_type() in ('CharField', 'TextField'):
        choices = getattr(fld, 'choices', None)
        if choices:
            display = value
            choices_map = dict(choices)
            key = value if value in choices_map else str(value)
            display = choices_map.get(key, value)
            return str(display)

    # Boolean
    if isinstance(value, bool):
        if value:
            return mark_safe('<span class="status_badge sucesso">Sim</span>')
        return mark_safe('<span class="status_badge neutro">Não</span>')

    # FK / one-to-one -> __str__ do relacionado
    if fld is not None and (fld.is_relation and fld.many_to_one):
        return escape(str(value))

    # Datas
    from datetime import date, datetime, time as dtime
    if isinstance(value, datetime):
        return date_format(value, 'd/m/Y H:i')
    if isinstance(value, date):
        return date_format(value, 'd/m/Y')
    if isinstance(value, dtime):
        return value.strftime('%H:%M')

    return escape(str(value))