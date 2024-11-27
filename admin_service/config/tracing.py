class TracingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.META.get('HTTP_X_REQUEST_ID', None)
        response = self.get_response(request)
        return response
