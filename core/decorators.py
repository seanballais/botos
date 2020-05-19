"""
Decorators based on the code by Elwin Arens in:
    https://stackoverflow.com/a/37601333/1116098
"""
from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url


def user_passes_test(
    test_func,
    next=None,
    login_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME
):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path() 
            resolved_next_url = resolve_url(next or path)
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                resolved_next_url, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def login_required(
    next=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=None
):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        next=next,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )

    return actual_decorator