from functools import wraps
from django.core.exceptions import PermissionDenied


def admin_or_hr_required(view_func):
    """
    Simple server-side permission check.

    Allows ADMIN and HR roles through. Everyone else (including EMPLOYEE,
    and anyone unauthenticated who somehow got past @login_required)
    gets a genuine 403 via Django's PermissionDenied, regardless of
    whether buttons are hidden in the template.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if request.user.role not in ('ADMIN', 'HR'):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
