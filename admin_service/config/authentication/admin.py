from django.contrib import admin

from config.authentication.auth_requests import check_permission


class PermissionAdmin(admin.ModelAdmin):
    resource_name = None

    def _check_permission(self, request, http_method):
        """Проверяет права и кэширует результат для текущего запроса."""
        if not hasattr(request, '_cached_permissions'):
            request._cached_permissions = {}

        cache_key = f"{self.resource_name}:{http_method}"
        if cache_key not in request._cached_permissions:
            access_token = request.session.get('access_token')
            if not access_token:
                request._cached_permissions[cache_key] = False
                return False

            request._cached_permissions[cache_key] = check_permission(request, access_token, self.resource_name,
                                                                      http_method)

        return request._cached_permissions[cache_key]

    def has_module_permission(self, request):
        return self._check_permission(request, 'get')

    def has_view_permission(self, request, obj=None):
        return self._check_permission(request, 'get')

    def has_add_permission(self, request):
        return self._check_permission(request, 'post')

    def has_change_permission(self, request, obj=None):
        return self._check_permission(request, 'put')

    def has_delete_permission(self, request, obj=None):
        return self._check_permission(request, 'delete')

    def get_model_perms(self, request):
        """Определяет права на уровне модели."""
        perms = super().get_model_perms(request)
        perms['view'] = self.has_view_permission(request)
        perms['add'] = self.has_add_permission(request)
        perms['change'] = self.has_change_permission(request)
        perms['delete'] = self.has_delete_permission(request)
        return perms
