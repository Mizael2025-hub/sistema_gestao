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
        # Se o widget já tem a classe aplicada (via form __init__), usa __str__
        # para preservar choices do SelectMultiple/Select (que dependem do
        # queryset resolvido pelo BoundField). Caso contrário, aplica via attrs.
        existing = field.field.widget.attrs.get('class', '')
        if css_class in existing:
            return str(field)
        # Junta classes em vez de sobrescrever.
        new_class = (existing + ' ' + css_class).strip() if existing else css_class
        return field.as_widget(attrs={**(field.field.widget.attrs or {}), 'class': new_class})
    return field


@register.filter(name='placeholder')
def placeholder(field, text):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={**(field.field.widget.attrs or {}), 'placeholder': text})
    return field


@register.filter(name='br_num')
def br_num(value, decimal_places=None):
    '''
    Formata número no padrão pt-BR: separador de milhar '.' e decimal ','.

    Uso: {{ valor|br_num }}              -> 1.234
         {{ valor|br_num:2 }}            -> 1.234,56
         {{ valor|default:'-'|br_num }}  -> respeita default quando vazio/zero

    Ex.: 1234567.89 -> 1.234.567,89 ; 1234 -> 1.234 ; 0 -> 0.
    Não localiza via Django L10N — monta a string explicitamente para
    garantir o formato pt-BR independentemente do locale ativo.
    '''
    if value is None or value == '':
        return value
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
    try:
        num = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return value
    if decimal_places is not None:
        quantizer = Decimal(1).scaleb(-int(decimal_places))
        num = num.quantize(quantizer, rounding=ROUND_HALF_UP)
    sign, digits, exp = num.as_tuple()
    s = format(num, 'f')
    neg = s.startswith('-')
    if neg:
        s = s[1:]
    if '.' in s:
        int_part, frac_part = s.split('.', 1)
    else:
        int_part, frac_part = s, ''
    groups = []
    while len(int_part) > 3:
        groups.insert(0, int_part[-3:])
        int_part = int_part[:-3]
    groups.insert(0, int_part)
    out = '.'.join(groups)
    if frac_part != '':
        out += ',' + frac_part
    if neg:
        out = '-' + out
    return out


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