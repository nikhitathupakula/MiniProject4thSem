from functools import wraps
from flask import redirect, url_for, current_app, jsonify, abort
from flask_login import current_user

def find_user_by_username(username):
    return current_app.db.officers.find_one({"off_name": username})

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return redirect(url_for('auth.login_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


