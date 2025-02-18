from functools import wraps

from django.http import HttpResponse
from django.shortcuts import redirect

from config.authentication.auth_requests import check_permission


def permission_required(resource: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            access_token = request.session.get('access_token')
            http_method = request.method

            if not access_token:
                return redirect('admin:index')

            if not check_permission(request, access_token, resource, http_method):
                return HttpResponse("У вас нет прав на просмотр этой страницы", status=403)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
