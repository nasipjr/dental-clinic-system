from functools import wraps
from flask import session, redirect, url_for, flash, g

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user:
                flash("Please log in to access this page.", "danger")
                return redirect(url_for('auth.login'))
            if g.current_user.role not in roles:
                flash("You do not have permission to access this page.", "danger")
                if g.current_user.role == 'patient':
                    return redirect(url_for('portal.dashboard'))
                return redirect(url_for('dashboard.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
