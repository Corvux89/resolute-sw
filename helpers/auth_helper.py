from functools import wraps
from flask import redirect, request, url_for
from flask_login import current_user

from models.exceptions import AdminAccessError


def is_admin(f=None):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.endpoint, provider="discord"))
            elif not current_user.is_admin:
                raise AdminAccessError("Admin access is required")
            return func(*args, **kwargs)

        return decorated_function

    # Callable functionality
    if f is None:
        return current_user.is_admin

    # Decorator functionality
    return decorator(f)
