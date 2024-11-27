from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from config.authentication.auth_requests import login_user, get_user_profile


User = get_user_model()


class AuthServiceBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        tokens = login_user(request, username, password)

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        if access_token and refresh_token:
            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token
            user_profile = get_user_profile(request, access_token)

            user, _ = User.objects.update_or_create(
                username=username,
                email=user_profile.get('email'),
                first_name=user_profile.get('first_name'),
                last_name=user_profile.get('last_name'),
                is_staff=True
            )
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
