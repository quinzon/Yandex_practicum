from config.authentication.auth_requests import check_permission, refresh_tokens
from django.core.exceptions import PermissionDenied


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.session.get('access_token')
        refresh_token = request.session.get('refresh_token')

        if access_token:
            self._handle_access_token(request, access_token, refresh_token)

        return self.get_response(request)

    def _handle_access_token(self, request, access_token, refresh_token):
        """Обрабатывает доступный access_token и обновляет его при необходимости."""
        if check_permission(request, access_token, 'admin', 'get'):
            self._refresh_tokens(request, refresh_token)

    def _refresh_tokens(self, request, refresh_token):
        """Обновляет access и refresh токены."""
        try:
            new_access_token, new_refresh_token = refresh_tokens(request, refresh_token)
            self._update_session_tokens(request, new_access_token, new_refresh_token)
        except PermissionDenied:
            request.session.flush()

    @staticmethod
    def _update_session_tokens(request, new_access_token, new_refresh_token):
        """Обновляет токены в сессии и в заголовках запроса."""
        request.session['access_token'] = new_access_token
        request.session['refresh_token'] = new_refresh_token
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
