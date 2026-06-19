from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            session.permanent = True
            flash(f"Welcome back, {user.first_name or user.username}!", "success")
            return redirect(url_for("dashboard.home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))
