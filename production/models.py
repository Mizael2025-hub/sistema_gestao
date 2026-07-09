'''
App production — apontamentos de produção.

Sprint 3: Teleiras — produção de grade (RF-T01..T04).
Sprint 4: Paradas de máquina (RF-P01..P04).

GridProduction com:
- data, operador, máquina, turno, modelo, polaridade, lote (3 dígitos),
  quantidade, hora início, hora fim.
- Lote automático 001..999 reinicia ao chegar em 999 (RF-T02).
- Cálculo de média de produção por hora (RF-T04 / RF-P03).

MachineStop:
- ligada a uma GridProduction (FK).
- stop_start / stop_end (hora que parou / hora que voltou).
- reasons: M2M para StopReason (RF-P02 — múltiplos motivos).
- note: observação opcional.
- Calcula stop_hours e impacta production_per_hour (RF-P03).
'''

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.models import TimestampedModel
from catalogs.models import GridModel, Machine, Polarity, Shift, StopReason


class GridProduction(TimestampedModel):
    '''Apontamento de produção de grade nas teleiras (UI "Produção de grade").'''

    production_date = models.DateField(_('data'), db_index=True)
    operator = models.ForeignKey(
        'operators.Operator', on_delete=models.PROTECT,
        related_name='grid_productions', verbose_name=_('operador'),
    )
    machine = models.ForeignKey(
        Machine, on_delete=models.PROTECT, related_name='grid_productions',
        verbose_name=_('máquina'),
    )
    shift = models.ForeignKey(
        Shift, on_delete=models.PROTECT, related_name='grid_productions',
        verbose_name=_('turno'),
    )
    grid_model = models.ForeignKey(
        GridModel, on_delete=models.PROTECT, related_name='grid_productions',
        verbose_name=_('modelo'),
    )
    polarity = models.CharField(
        _('polaridade'), max_length=3, choices=Polarity.choices,
    )
    lot = models.CharField(
        _('lote'), max_length=3,
        help_text=_('Lote de 3 dígitos (001–999). Preenchido automaticamente.'),
    )
    quantity = models.PositiveIntegerField(_('quantidade'))
    start_time = models.DateTimeField(_('hora início'))
    end_time = models.DateTimeField(_('hora fim'))

    class Meta:
        verbose_name = _('produção de grade')
        verbose_name_plural = _('produções de grade')
        ordering = ('-production_date', '-start_time')
        indexes = [
            models.Index(fields=('production_date', 'machine')),
            models.Index(fields=('lot',)),
            models.Index(fields=('polarity',)),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='grid_prod_end_after_start',
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='grid_prod_quantity_positive',
            ),
        ]

    def __str__(self):
        return '%s · %s · %s (%s)' % (
            self.production_date.strftime('%d/%m/%Y'),
            self.machine.name, self.grid_model.name, self.lot,
        )

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': _('Hora fim deve ser maior que a hora início.')})
        if self.lot and (not self.lot.isdigit() or not (1 <= int(self.lot) <= 999)):
            raise ValidationError({'lot': _('Lote deve ter 3 dígitos entre 001 e 999.')})

    # ---- Lote automático 3 dígitos (RF-T02) ---------------------------
    @classmethod
    def next_lot(cls):
        '''
        Próximo lote sequencial de 3 dígitos (001–999).
        Reinicia em 001 ao chegar em 999.

        Lógica: maior lote já usado (qualquer data) + 1; ao passar de 999,
        volta para 001. A query usa cast_text → zero-padded para garantir
        ordenação lexical correta de 3 dígitos com leading zeros.
        '''
        with transaction.atomic():
            last = cls.objects.order_by('-lot').first()
            if not last or not last.lot.isdigit():
                return '001'
            nxt = int(last.lot) + 1
            if nxt > 999:
                return '001'
            return '%03d' % nxt

    def save(self, *args, **kwargs):
        if not self.lot:
            self.lot = self.next_lot()
        if isinstance(self.lot, int):
            self.lot = '%03d' % self.lot
        super().save(*args, **kwargs)

    # ---- Métricas (RF-T04) --------------------------------------------
    @property
    def duration_hours(self):
        '''Horas trabalhadas (hora fim − hora início).'''
        if not self.start_time or not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600.0

    @property
    def stop_hours(self):
        '''Soma de horas paradas vinculadas (RF-P03).'''
        stops = getattr(self, 'stops', None)
        total = 0
        if stops is None:
            return total
        for stop in stops.all():
            total += stop.duration_hours
        return total

    @property
    def effective_hours(self):
        '''Horas líquidas (= trabalhadas − paradas).'''
        return max(self.duration_hours - self.stop_hours, 0)

    @property
    def production_per_hour(self):
        '''Média de produção por hora (líquido de paradas) — RF-T04 / RF-P03.'''
        eff = self.effective_hours
        if eff <= 0:
            return 0
        return round(self.quantity / eff, 2)


class MachineStop(TimestampedModel):
    '''
    Parada de máquina vinculada a um apontamento de produção de grade.

    RF-P01: registrada após localizar a produção por data/operador/máquina.
    RF-P02: motivos múltiplos (M2M para StopReason).
    RF-P03: impacta a média de produção por hora via GridProduction.stop_hours.
    '''

    grid_production = models.ForeignKey(
        GridProduction, on_delete=models.CASCADE, related_name='stops',
        verbose_name=_('produção de grade'),
    )
    stop_start = models.DateTimeField(_('hora que parou'), db_index=True)
    stop_end = models.DateTimeField(_('hora que voltou'), db_index=True)
    reasons = models.ManyToManyField(
        StopReason, related_name='machine_stops',
        verbose_name=_('motivo(s)'),
        help_text=_('Múltiplos motivos podem ser selecionados (RF-P02).'),
    )
    note = models.TextField(_('observação'), blank=True, default='')

    class Meta:
        verbose_name = _('parada de máquina')
        verbose_name_plural = _('paradas de máquina')
        ordering = ('-stop_start',)
        indexes = [
            models.Index(fields=('stop_start', 'stop_end')),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(stop_end__gt=models.F('stop_start')),
                name='machine_stop_end_after_start',
            ),
        ]

    def __str__(self):
        from django.utils.timezone import localtime
        start = localtime(self.stop_start) if self.stop_start else None
        end = localtime(self.stop_end) if self.stop_end else None
        return 'Parada · %s · %s–%s' % (
            self.grid_production,
            start.strftime('%H:%M') if start else '—',
            end.strftime('%H:%M') if end else '—',
        )

    def clean(self):
        super().clean()
        if self.stop_start and self.stop_end and self.stop_end <= self.stop_start:
            raise ValidationError({'stop_end': _('Hora que voltou deve ser maior que a hora que parou.')})
        # A parada deve estar contida no intervalo do apontamento.
        gp = self.grid_production
        if gp and gp.start_time and gp.end_time:
            if self.stop_start and (self.stop_start < gp.start_time):
                raise ValidationError({'stop_start': _('A parada não pode iniciar antes do apontamento (%s).' % gp.start_time.strftime('%d/%m/%Y %H:%M'))})
            if self.stop_end and (self.stop_end > gp.end_time):
                raise ValidationError({'stop_end': _('A parada não pode terminar depois do apontamento (%s).' % gp.end_time.strftime('%d/%m/%Y %H:%M'))})

    @property
    def duration_hours(self):
        '''Duração da parada em horas.'''
        if not self.stop_start or not self.stop_end or self.stop_end <= self.stop_start:
            return 0
        return round((self.stop_end - self.stop_start).total_seconds() / 3600.0, 4)

    @property
    def duration_label(self):
        '''Rótulo amigável da duração (ex.: 1h 30min).'''
        seconds = 0
        if self.stop_start and self.stop_end and self.stop_end > self.stop_start:
            seconds = (self.stop_end - self.stop_start).total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours and minutes:
            return '%dh %dmin' % (hours, minutes)
        if hours:
            return '%dh' % hours
        if minutes:
            return '%dmin' % minutes
        return '0min'

    @property
    def reasons_display(self):
        '''Lista os motivos separados por vírgula.'''
        return ', '.join(str(r) for r in self.reasons.all()) or '—'