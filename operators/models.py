'''
App operators — cadastro de operadores (RF-C01 / RF-U03).

Operator (UI "Operador") é uma entidade de domínio ligada opcionalmente a
um usuário (User) para futuro apontamento de consumo de chumbo por
operador. Campos: nome, matrícula (opcional), ativo.
'''

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import ActiveModel


class Operator(ActiveModel):
    '''
    Operador de chão de fábrica.

    - name: nome do operador (UI "Nome").
    - user: vínculo opcional com User (auth nativa) — futuro apontamento
      de consumo de chumbo por operador (RF-U03).
    '''

    name = models.CharField(_('nome'), max_length=120)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operator_profile',
        verbose_name=_('usuário'),
        help_text=_('Vínculo opcional com usuário do sistema (login).'),
    )

    class Meta:
        verbose_name = _('operador')
        verbose_name_plural = _('operadores')
        ordering = ('name',)
        indexes = [
            models.Index(fields=('name',)),
        ]

    def __str__(self):
        return self.name