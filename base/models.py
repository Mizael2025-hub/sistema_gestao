'''
Models abstratos e utilitários compartilhados por todos os apps.

Todo model de domínio herda de TimestampedModel, garantindo created_at e
updated_at (RNF e Sprint 2).
'''

from django.db import models


class TimestampedModel(models.Model):
    '''Base abstrata com created_at e updated_at.'''

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='atualizado em')

    class Meta:
        abstract = True


class IsActiveManager(models.Manager):
    '''Manager que expõe only_active() para modelos com flag is_active.'''

    def only_active(self):
        return self.filter(is_active=True)


class ActiveModel(TimestampedModel):
    '''
    Base abstrata para entidades de cadastro que possuem flag is_active.
    '''

    is_active = models.BooleanField(default=True, verbose_name='ativo')

    objects = IsActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True