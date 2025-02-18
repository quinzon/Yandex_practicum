from django.core.exceptions import BadRequest
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from config.authentication.views import permission_required
from config.authentication.auth_requests import get_users, find_user


@permission_required(resource='profiles')
def profiles(request) -> HttpResponse:
    return render(request, 'profiles.html')


@permission_required(resource='profiles')
def get_profiles(request) -> JsonResponse:
    """Обрабатывает AJAX-запросы для получения профилей с пагинацией и фильтрацией по роли."""
    page_number = request.GET.get('page_number', 1)
    page_size = request.GET.get('page_size', 25)
    role_name = request.GET.get('role_name')
    access_token = request.session.get('access_token')

    params = {'page_number': page_number, 'page_size': page_size}
    if role_name:
        params['role_name'] = role_name

    users_data = get_users(request, access_token, params)
    results = users_data.get('items', [])
    total_results = users_data.get('meta', {}).get('total_items', 0)
    meta_data = users_data.get('meta', {})

    return JsonResponse({
        'results': results,
        'total_results': total_results,
        'page_number': int(page_number),
        'page_size': int(page_size),
        'meta': meta_data,
    })


@permission_required(resource='profiles')
def find_profile(request) -> JsonResponse:
    """Обрабатывает AJAX-запросы для получения профиля по запросу."""
    email = request.GET.get('query')
    access_token = request.session.get('access_token')
    if email:
        user_data = find_user(request, access_token, {'email': email})
        return JsonResponse({'results': user_data})
    raise BadRequest('Неверные параметры запроса')
