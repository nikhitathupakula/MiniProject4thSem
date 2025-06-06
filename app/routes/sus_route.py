from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import current_app as app

sus_bp = Blueprint('suspects', __name__)

@sus_bp.route('/victims_suspects', methods=['GET', 'POST'])
@login_required
def manage_victims_suspects():

    if request.method == 'POST':
        if request.form.get('type') == 'victim':
            data = {
                "vic_name": request.form['vic_name'],
                "vic_contact": request.form['vic_contact'],
                "vic_address": request.form['vic_address']
            }
            app.db["victims"].insert_one(data)
            flash("Victim added successfully!", "success")

        elif request.form.get('type') == 'suspect':
            data = {
                "sus_name": request.form['sus_name'],
                "sus_contact": request.form['sus_contact'],
                "sus_address": request.form['sus_address'],
                "sus_email": request.form['sus_email'],
                "sus_status": request.form['sus_status']
            }
            app.db["suspects"].insert_one(data)
            flash("Suspect added successfully!", "success")

        return redirect(url_for('suspects.manage_victims_suspects'))

    victims = list(app.db["victims"].find())
    suspects = list(app.db["suspects"].find())

    return render_template('suspects.html', victims=victims, suspects=suspects)
