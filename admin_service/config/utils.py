from django.http import HttpRequest


def prepare_headers(request: HttpRequest, headers: dict | None = None) -> dict:
    """Подготавливает заголовки для HTTP-запроса."""
    if headers is None:
        headers = {}
    request_id = getattr(request, 'request_id', None)
    headers['x-request-id'] = request_id
    return headers
