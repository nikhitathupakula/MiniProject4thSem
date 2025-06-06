from functools import wraps
from flask import abort
from flask_login import current_user

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if current_user.is_authenticated and current_user.role in roles:
                return f(*args, **kwargs)
            abort(403)
        return decorated_view
    return wrapper
