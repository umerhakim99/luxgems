from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from accounts.utils import user_is_admin_role


def admin_role_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not u.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        if not user_is_admin_role(u):
            messages.error(request, "You do not have permission to access the admin dashboard.")
            return redirect("catalog:home")
        return view_func(request, *args, **kwargs)

    return _wrapped


def customer_dashboard_required(view_func):
    """Logged-in customers (non-admin storefront dashboard). Admins can still open if needed."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        return view_func(request, *args, **kwargs)

    return _wrapped
