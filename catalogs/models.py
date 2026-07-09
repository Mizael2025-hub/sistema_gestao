'''
App catalogs — cadastros-base (Sprint 2 / RF-C02..C08).

Modelos de catálogo compartilhados por toda a aplicação:

- Shift (UI "Turno"): nome, hora início, hora fim.
- Sector (UI "Setor"): teleiras, boleira, moinho, masseira, empastadeira,
  montagem, formação. Fixo/seed.
- Machine (UI "Máquina"): teleiras e demais máquinas; vínculo com setor.
- GridModel (UI "Modelo"): modelos de bateria e placas; B5L e B7B
  compartilham grade (shares_grid_with).
- Polarity: choices POSITIVE/NEGATIVE.
- LeadAlloy (UI "Liga"): Liga 0/4/5/6 com cor associada (seed).
- StopReason (UI "Motivo da parada"): motivos categorizados.

Todos herdam base.ActiveModel (created_at/updated_at + is_active).
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import ActiveModel


# --------------------------------------------------------------------- #
# Polarity (choices — RF-C04)
# --------------------------------------------------------------------- #
class Polarity(models.TextChoices):
    POSITIVE = 'POS', _('Positiva')
    NEGATIVE = 'NEG', _('Negativa')


# --------------------------------------------------------------------- #
# LeadAlloy — códigos de liga (RF-C07)
# --------------------------------------------------------------------- #
class AlloyCode(models.TextChoices):
    LIGA_0 = 'LIGA_0', _('Liga 0 — Chumbo puro')
    LIGA_4 = 'LIGA_4', _('Liga 4 — Pb+Estanho')
    LIGA_5 = 'LIGA_5', _('Liga 5 — Negativa')
    LIGA_6 = 'LIGA_6', _('Liga 6 — Positiva')


class LeadAlloy(ActiveModel):
    code = models.CharField(_('código'), max_length=16, unique=True, choices=AlloyCode.choices)
    name = models.CharField(_('nome'), max_length=60)
    color = models.CharField(_('cor'), max_length=9, default='#1D1D1F')

    class Meta:
        verbose_name = _('liga de chumbo')
        verbose_name_plural = _('ligas de chumbo')
        ordering = ('code',)

    def __str__(self):
        return self.name


# --------------------------------------------------------------------- #
# Sector (RF-C06)
# --------------------------------------------------------------------- #
class Sector(ActiveModel):
    name = models.CharField(_('nome'), max_length=80, unique=True)

    class Meta:
        verbose_name = _('setor')
        verbose_name_plural = _('setores')
        ordering = ('name',)

    def __str__(self):
        return self.name


# --------------------------------------------------------------------- #
# Machine (RF-C05) — teleiras, empastadeira, etc.
# --------------------------------------------------------------------- #
class Machine(ActiveModel):
    name = models.CharField(_('nome/número'), max_length=80)
    sector = models.ForeignKey(
        Sector, on_delete=models.PROTECT, related_name='machines',
        verbose_name=_('setor'),
    )

    class Meta:
        verbose_name = _('máquina')
        verbose_name_plural = _('máquinas')
        ordering = ('name',)
        indexes = [models.Index(fields=('sector',))]
        constraints = [
            models.UniqueConstraint(fields=('name', 'sector'), name='unique_machine_per_sector')
        ]

    def __str__(self):
        return '%s · %s' % (self.name, self.sector.name)


# --------------------------------------------------------------------- #
# Shift (RF-C02)
# --------------------------------------------------------------------- #
class Shift(ActiveModel):
    name = models.CharField(_('nome'), max_length=60)
    is_overtime = models.BooleanField(
        _('hora extra'), default=False,
        help_text=_('Marque quando for um turno de hora extra. Nesse caso, os horários de início e fim ficam opcionais e podem ser definidos no apontamento.'),
    )
    start_time = models.TimeField(_('hora início'), null=True, blank=True)
    end_time = models.TimeField(_('hora fim'), null=True, blank=True)

    class Meta:
        verbose_name = _('turno')
        verbose_name_plural = _('turnos')
        ordering = ('start_time', 'name')

    def __str__(self):
        if self.is_overtime:
            return '%s (hora extra)' % self.name
        if self.start_time and self.end_time:
            return '%s (%s–%s)' % (self.name, self.start_time.strftime('%H:%M'), self.end_time.strftime('%H:%M'))
        return self.name


# --------------------------------------------------------------------- #
# GridModel (RF-C03) — modelos de bateria
# --------------------------------------------------------------------- #
class GridModel(ActiveModel):
    name = models.CharField(_('nome'), max_length=40, unique=True)
    common_name = models.CharField(_('nome comum'), max_length=60, blank=True, default='')
    positive_plates = models.PositiveSmallIntegerField(_('placas positivas'), default=18)
    negative_plates = models.PositiveSmallIntegerField(_('placas negativas'), default=24)
    shares_grid_with = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='shared_grid_models',
        verbose_name=_('compartilha grade com'),
        help_text=_('Ex.: B5L e B7B usam a mesma grade.'),
    )

    class Meta:
        verbose_name = _('modelo de grade')
        verbose_name_plural = _('modelos de grade')
        ordering = ('name',)

    def __str__(self):
        return self.name


# --------------------------------------------------------------------- #
# StopReason (RF-C08) — motivos de parada categorizados
# --------------------------------------------------------------------- #
class StopReasonCategory(models.TextChoices):
    MECHANICAL = 'MECHANICAL', _('Mecânica')
    ELECTRICAL = 'ELECTRICAL', _('Elétrica')
    MATERIAL = 'MATERIAL', _('Material/matéria-prima')
    OPERATIONAL = 'OPERATIONAL', _('Operacional')
    QUALITY = 'QUALITY', _('Qualidade')
    SETUP = 'SETUP', _('Setup/troca')
    OTHER = 'OTHER', _('Outro')


class StopReason(ActiveModel):
    code = models.CharField(_('código'), max_length=30, blank=True, default='')
    description = models.CharField(_('descrição'), max_length=160)
    category = models.CharField(
        _('categoria'), max_length=20,
        choices=StopReasonCategory.choices, default=StopReasonCategory.OTHER,
    )

    class Meta:
        verbose_name = _('motivo de parada')
        verbose_name_plural = _('motivos de parada')
        ordering = ('category', 'description')
        indexes = [models.Index(fields=('category',))]

    def __str__(self):
        if self.code:
            return '%s · %s' % (self.code, self.description)
        return self.description