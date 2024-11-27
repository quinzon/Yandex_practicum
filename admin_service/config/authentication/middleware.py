from config.authentication.auth_requests import check_permission, refresh_tokens
from django.core.exceptions import PermissionDenied


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.session.get('access_token')
        refresh_token = request.session.get('refresh_token')

        if access_token:
            if check_permission(access_token, 'admin', 'get'):
                try:
                    new_access_token, new_refresh_token = refresh_tokens(refresh_token)
                    request.session['access_token'] = new_access_token
                    request.session['refresh_token'] = new_refresh_token
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                except PermissionDenied:
                    request.session.flush()
        return self.get_response(request)
