from functools import wraps
from flask import session, redirect, url_for, flash, g, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
            msg = "يرجى تسجيل الدخول للوصول إلى هذه الصفحة." if is_ar else "Please log in to access this page."
            flash(msg, "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user:
                is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
                msg = "يرجى تسجيل الدخول للوصول إلى هذه الصفحة." if is_ar else "Please log in to access this page."
                flash(msg, "danger")
                return redirect(url_for('auth.login'))
            if g.current_user.role not in roles:
                is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
                msg = "ليس لديك صلاحية للوصول إلى هذه الصفحة." if is_ar else "You do not have permission to access this page."
                flash(msg, "danger")
                if g.current_user.role == 'patient':
                    return redirect(url_for('portal.dashboard'))
                return redirect(url_for('dashboard.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
