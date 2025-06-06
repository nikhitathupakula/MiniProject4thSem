from flask import Blueprint, redirect, url_for, request, render_template, flash, current_app
from flask_login import login_required
from app.models import (
    get_all_evidence,
    get_evidence_by_id,
    update_evidence,
    add_evidence
)
import traceback

evidence_bp = Blueprint('evidence', __name__, url_prefix='/dashboard')

@evidence_bp.route('/manage_evidence', methods=['GET', 'POST'])
@login_required
def manage_evidence():
    if request.method == 'POST':
        try:
            new_evidence = {
                'evidence_type': request.form.get('evidence_type', '').strip(),
                'collected_by': request.form.get('collected_by', '').strip() or None,
                'storage_location': request.form.get('storage_location', '').strip() or None,
                'file_url': request.form.get('file_url', '').strip() or None,
                'description': request.form.get('description', '').strip() or None,
                'status': request.form.get('status', 'Collected').strip()
            }

            if not new_evidence['evidence_type']:
                flash("Evidence Type is required.", "danger")
            else:
                add_evidence(new_evidence)
                flash("Evidence added successfully.", "success")
                return redirect(url_for('evidence.manage_evidence'))

        except Exception as e:
            traceback.print_exc()
            flash(f"Error uploading evidence: {str(e)}", "danger")

    try:
        evidence_list = get_all_evidence()
    except Exception as e:
        traceback.print_exc()
        flash(f"Error retrieving evidence list: {str(e)}", "danger")
        evidence_list = []

    return render_template('evidence.html', evidence_list=evidence_list)

@evidence_bp.route('/edit/<evidence_id>', methods=['GET', 'POST'])
@login_required
def edit_evidence(evidence_id):
    try:
        evidence = get_evidence_by_id(evidence_id)
        if not evidence:
            flash("Evidence not found.", "warning")
            return redirect(url_for('evidence.manage_evidence'))
    except Exception as e:
        traceback.print_exc()
        flash(f"Error loading evidence: {str(e)}", "danger")
        return redirect(url_for('evidence.manage_evidence'))

    if request.method == 'POST':
        updated_fields = {}
        for field in ['status', 'storage_location', 'file_url', 'description']:
            form_value = request.form.get(field)
            if form_value and form_value != evidence.get(field):
                updated_fields[field] = form_value.strip()

        if updated_fields:
            try:
                update_evidence(evidence_id, updated_fields)
                flash("Evidence updated successfully.", "success")
            except Exception as e:
                traceback.print_exc()
                flash(f"Error updating evidence: {str(e)}", "danger")
        else:
            flash("No changes made.", "info")

        return redirect(url_for('evidence.manage_evidence'))

    return render_template('update-evidence.html', evidence=evidence)

@evidence_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_evidence_form():
    try:
        officers = list(current_app.db.officers.find({}, {"_id": 0, "off_name": 1}))
    except Exception as e:
        traceback.print_exc()
        flash(f"Error loading officers: {str(e)}", "danger")
        officers = []

    statuses = ['Collected', 'Analyzed', 'Archived']

    if request.method == 'POST':
        try:
            new_evidence = {
                'evidence_type': request.form.get('evidence_type', '').strip(),
                'collected_by': request.form.get('collected_by', '').strip() or None,
                'storage_location': request.form.get('storage_location', '').strip() or None,
                'file_url': request.form.get('file_url', '').strip() or None,
                'description': request.form.get('description', '').strip() or None,
                'status': request.form.get('status', 'Collected').strip()
            }

            if not new_evidence['evidence_type']:
                flash("Evidence Type is required.", "danger")
                return redirect(url_for('evidence.add_evidence_form'))

            add_evidence(new_evidence)
            flash("Evidence added successfully.", "success")
            return redirect(url_for('evidence.manage_evidence'))

        except Exception as e:
            traceback.print_exc()
            flash(f"Error adding evidence: {str(e)}", "danger")
            return redirect(url_for('evidence.add_evidence_form'))

    return render_template("add_evidence.html", officers=officers, statuses=statuses)
