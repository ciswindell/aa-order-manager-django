"""
Middleware to capture the current authenticated user into thread-local storage
so that model signal handlers can access it when enqueuing background tasks.
"""

from django.utils.deprecation import MiddlewareMixin
from .utils.current_user import set_current_user, clear_current_user


class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):  # pragma: no cover
        set_current_user(getattr(request, "user", None))

    def process_response(self, request, response):  # pragma: no cover
        clear_current_user()
        return response

    def process_exception(self, request, exception):  # pragma: no cover
        clear_current_user()
        return None
