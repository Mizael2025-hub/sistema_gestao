'''
Context processor base: itens globais da UI (marca, ano, user).
'''

from django.conf import settings


def base_context(request):
    return {
        'app_name': 'PCP Komotors',
        'app_short': 'PCP',
        'app_version': getattr(settings, 'APP_VERSION', '1.0.0'),
    }