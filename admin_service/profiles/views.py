from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from config.authentication.views import permission_required
from config.authentication.auth_requests import get_users


@permission_required(resource='profiles')
def profiles(request) -> HttpResponse:
    return render(request, 'profiles.html')


@permission_required(resource='profiles')
def search_profiles(request) -> JsonResponse:
    """Обрабатывает AJAX-запросы для получения профилей с пагинацией."""
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 25)
    query = request.GET.get('query')
    role = request.GET.get('role')
    access_token = request.session.get('access_token')

    params = {'page': page, 'page_size': page_size}
    if query:
        params['query'] = query
    if role:
        params['role'] = role

    users_data = get_users(request, access_token, params)
    results = users_data.get('results', [])
    total_results = users_data.get('total_results', 0)

    return JsonResponse({
        'results': results,
        'total_results': total_results,
        'page': int(page),
        'page_size': int(page_size)
    })
