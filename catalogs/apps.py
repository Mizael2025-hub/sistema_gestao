'''App config do catalogs.'''
from django.apps import AppConfig


class CatalogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogs'
    verbose_name = 'Cadastros-base'