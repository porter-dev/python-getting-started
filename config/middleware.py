from django.http import HttpResponse


class HealthCheckMiddleware:
    """
    - Answers /healthz before host validation, so probes that address the pod by IP
      pass even when DJANGO_ALLOWED_HOSTS is restricted.
    - Touches no database or other dependency.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/healthz':
            return HttpResponse('ok', content_type='text/plain')
        return self.get_response(request)
