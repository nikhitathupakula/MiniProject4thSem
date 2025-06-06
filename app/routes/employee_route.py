from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import current_app as app
import bcrypt
from datetime import datetime

employee_bp = Blueprint('employee', __name__)

from datetime import datetime

@employee_bp.route('/employees', methods=['GET', 'POST'])
@login_required
def manage_employees():
    if current_user.role != 'Admin':
        return "Access Denied", 403

    if request.method == 'POST':
        raw_password = request.form['password']
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        joined_at_str = request.form['joined_at']
        joined_at = datetime.strptime(joined_at_str, '%Y-%m-%d')

        data = {
            "off_name": request.form['name'],
            "email": request.form['email'],
            "role_name": request.form['role'],
            "phone": request.form['phone'],
            "joined_at": joined_at,
            "hashed_pass": hashed_password
        }

        app.db["officers"].insert_one(data)
        flash("Employee added successfully!")
        return redirect(url_for('employee.manage_employees'))

    employees = list(app.db["officers"].find())
    return render_template('employees.html', employees=employees)
