from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from myapp.models import Account

class EmailVerficationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            account = Account.objects.get(user=user)
            if account.email_verified and user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None