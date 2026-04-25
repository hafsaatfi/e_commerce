from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return _wrapped_view