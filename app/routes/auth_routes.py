from flask import Blueprint, request, render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("auth.login_page"))

@auth_bp.route("/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_home"))
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    user = User.get_by_username(email)
    if user and user.verify_password(password):
        login_user(user, remember=True)
        
        session['role'] = user.role
        return redirect(url_for("dashboard.dashboard_home"))

    return render_template("login.html", error="Invalid credentials")

@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))
