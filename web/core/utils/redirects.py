"""Helpers and decorators for safe 'redirect back' behavior."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


SESSION_KEY = "post_oauth_next"


def resolve_next_url(
    request: HttpRequest,
    default_name: str = "integrations:manage",
    pop_session: bool = True,
) -> str:
    """Resolve a safe next URL from ?next, session, or Referer; fall back to default route.

    - Uses Django's host/HTTPS checks to avoid open redirects.
    - When pop_session=True, clears the stored session key.
    """
    candidate = request.GET.get("next")
    if not candidate and pop_session:
        candidate = request.session.pop(SESSION_KEY, None)
    if not candidate:
        candidate = request.META.get("HTTP_REFERER")
    if candidate and url_has_allowed_host_and_scheme(
        candidate, {request.get_host()}, request.is_secure()
    ):
        return candidate
    if default_name == "__root__":
        return "/"
    return reverse(default_name)


def store_next(param: str = "next", session_key: str = SESSION_KEY) -> Callable:
    """Decorator for 'start' views to stash the next URL in session before redirecting out."""

    def deco(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            candidate = request.GET.get(param) or request.META.get("HTTP_REFERER")
            if candidate and url_has_allowed_host_and_scheme(
                candidate, {request.get_host()}, request.is_secure()
            ):
                request.session[session_key] = candidate
            return view_func(request, *args, **kwargs)

        return _wrapped

    return deco


def redirect_back(
    default_name: str = "integrations:manage", pop_session: bool = True
) -> Callable:
    """Decorator for 'finish' views to redirect the user back after success.

    - Respects explicit HttpResponseRedirect returned by the view.
    - Otherwise issues a redirect to resolved next URL.
    """

    def deco(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            response = view_func(request, *args, **kwargs)
            if isinstance(response, HttpResponseRedirect):
                return response
            return HttpResponseRedirect(
                resolve_next_url(
                    request, default_name=default_name, pop_session=pop_session
                )
            )

        return _wrapped

    return deco


__all__ = [
    "SESSION_KEY",
    "resolve_next_url",
    "store_next",
    "redirect_back",
]
