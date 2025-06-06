from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from bson import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard_home():
    print(f"Current user's role: {current_user.role}")
    return render_template("dashboard.html", role=current_user.role)