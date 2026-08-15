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


def get_safe_redirect_url(default_endpoint=None, **kwargs):
    """Returns next_url if safe and local, otherwise falls back to default_endpoint."""
    from urllib.parse import urlparse
    next_url = request.form.get("next") or request.args.get("next") or request.referrer
    if next_url:
        try:
            ref_url = urlparse(next_url)
            host_url = urlparse(request.host_url)
            if not ref_url.netloc or ref_url.netloc == host_url.netloc:
                path = ref_url.path.lower()
                # Exclude self loops (form pages themselves)
                if not any(k in path for k in ["/edit", "/delete"]):
                    return next_url
        except Exception:
            pass
    if default_endpoint:
        return url_for(default_endpoint, **kwargs)
    return url_for("appointments.appointments")

