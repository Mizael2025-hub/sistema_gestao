'''
Backend de autenticação por email.

Permite login com email ao invés de username. Usa a auth nativa do Django
(RF-U02). Mantém usernames compatíveis como fallback.
'''

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailBackend(ModelBackend):
    '''Autentica usuário por email ou username.'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).order_by('id').first()

        if user is None or not user.check_password(password):
            return None
        if not self.user_can_authenticate(user):
            return None
        return user