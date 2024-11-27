from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
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

            request._cached_permissions[cache_key] = check_permission(access_token, self.resource_name, http_method)

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


@admin.register(Genre)
class GenreAdmin(PermissionAdmin):
    resource_name = 'admin:genre'
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(PermissionAdmin):
    resource_name = 'admin:person'
    search_fields = ('full_name',)


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    autocomplete_fields = ('genre',)


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ('person',)


@admin.register(FilmWork)
class FilmWorkAdmin(PermissionAdmin):
    resource_name = 'admin:filmwork'
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)
    list_display = ('title', 'type', 'creation_date', 'rating', 'get_genres')
    list_filter = ('type', 'genres')
    search_fields = ('title', 'description', 'id')

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related('genres')
        return queryset

    def get_genres(self, obj):
        return ','.join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = _('genres')
