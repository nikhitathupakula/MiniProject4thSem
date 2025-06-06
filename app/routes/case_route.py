from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash, jsonify
from flask_login import current_user, login_required
from bson import ObjectId
import datetime
from functools import wraps

case_bp = Blueprint('cases', __name__, url_prefix='/cases')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash("Unauthorized access.", "danger")
            return redirect(url_for('cases.list_cases'))
        return f(*args, **kwargs)
    return decorated_function


from bson import ObjectId

@case_bp.route('/')
@login_required
def list_cases():
    search_term = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10

    query = {}
    if search_term:
        query = {
            '$or': [
                {'case_number': {'$regex': search_term, '$options': 'i'}},
                {'case_title': {'$regex': search_term, '$options': 'i'}},
                {'status': {'$regex': search_term, '$options': 'i'}}
            ]
        }

    total_cases = current_app.db.cases.count_documents(query)
    cases = list(current_app.db.cases.find(query)
        .skip((page - 1) * per_page)
        .limit(per_page)
        .sort('created_at', -1))

    officer_ids = list({
        ObjectId(case['officer_id']) if isinstance(case['officer_id'], str) else case['officer_id']
        for case in cases if 'officer_id' in case
    })

    officers = current_app.db.officers.find(
        {'_id': {'$in': officer_ids}},
        {'_id': 1, 'off_name': 1}
    )
    officer_map = {off['_id']: off['off_name'] for off in officers}


    for case in cases:
        raw_id = case.get('officer_id')
        normalized_id = ObjectId(raw_id) if isinstance(raw_id, str) else raw_id
        case['officer_name'] = officer_map.get(normalized_id, 'Unknown')
        if 'created_at' in case:
            if isinstance(case['created_at'], str):
                try:
                    case['created_at'] = datetime.datetime.strptime(case['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    case['created_at'] = datetime.datetime.utcnow()

    return render_template('cases.html',
                           cases=cases,
                           page=page,
                           per_page=per_page,
                           total_cases=total_cases)

@case_bp.route('/add_case', methods=['GET'])
@login_required
@admin_required
def add_case_form():
    officers = list(current_app.db.officers.find({}, {"_id": 1, "off_name": 1}))
    return render_template("add_cases.html", officers=officers)

@case_bp.route('/add_case', methods=['POST'])
@login_required
@admin_required
def add_case():
    case_data = {
        "case_number": request.form['case_number'],
        "case_title": request.form['case_title'],
        "status": request.form['status'],
        "officer_id": ObjectId(request.form['officer_id']),
        "description": request.form.get('description', ''),
        "notes": request.form.get('notes', ''),
        "victim": {
            "name": request.form.get('vic_name'),
            "contact": request.form.get('vic_contact'),
            "address": request.form.get('vic_address')
        },
        "evidence_ids": [request.form.get('evidenceId')] if request.form.get('evidenceId') else [],
        "suspect_ids": [request.form.get('suspectId')] if request.form.get('suspectId') else [],
        "created_at": datetime.datetime.utcnow(),
        "created_by": session.get('user_id')
    }

    current_app.db.cases.insert_one(case_data)
    flash("Case created successfully", "success")
    return redirect(url_for('cases.list_cases'))

@case_bp.route('/view/<case_id>')
@login_required
def view_case(case_id):
    try:
        case = current_app.db.cases.find_one({"_id": ObjectId(case_id)})
        if not case:
            flash("Case not found.", "danger")
            return redirect(url_for('cases.list_cases'))
        
        officer = current_app.db.officers.find_one({"_id": ObjectId(case.get("officer_id"))})
        case['officer_name'] = officer['off_name'] if officer else 'Unknown'

        return render_template("view_case.html", case=case)
    except Exception as e:
        print(f"Error fetching case: {e}")
        flash("Error loading case details.", "danger")
        return redirect(url_for('cases.list_cases'))
    
@case_bp.route('/edit/<case_id>', methods=['GET'])
@login_required
@admin_required
def edit_case_form(case_id):
    case = current_app.db.cases.find_one({"_id": ObjectId(case_id)})
    if not case:
        flash("Case not found.", "danger")
        return redirect(url_for('cases.list_cases'))

    officers = list(current_app.db.officers.find({}, {"_id": 1, "off_name": 1}))
    return render_template("edit_cases.html", case=case, officers=officers)

@case_bp.route('/edit/<case_id>', methods=['POST'])
@login_required
@admin_required
def edit_case(case_id):
    case = current_app.db.cases.find_one({"_id": ObjectId(case_id)})
    if not case:
        flash("Case not found.", "danger")
        return redirect(url_for('cases.list_cases'))

    def form_or_existing(field_name, existing_value):
        form_val = request.form.get(field_name)
        return form_val if form_val and form_val != str(existing_value) else existing_value

    updated_fields = {}

    new_status = request.form.get('status')
    if new_status and new_status != case.get('status'):
        updated_fields['status'] = new_status

    new_officer_id = request.form.get('assignedOfficer')
    if new_officer_id:
        try:
            new_officer_obj_id = ObjectId(new_officer_id)
            if case.get('officer_id') != new_officer_obj_id:
                updated_fields['officer_id'] = new_officer_obj_id
        except Exception:
            flash("Invalid officer ID.", "danger")
            return redirect(url_for('cases.edit_case_form', case_id=case_id))

    new_description = request.form.get('description')
    if new_description is not None and new_description != case.get('description'):
        updated_fields['description'] = new_description

    victim = case.get('victim', {})
    new_vic_name = request.form.get('vic_name')
    if new_vic_name and new_vic_name != victim.get('name'):
        updated_fields['victim.name'] = new_vic_name

    new_vic_contact = request.form.get('vic_contact')
    if new_vic_contact and new_vic_contact != victim.get('contact'):
        updated_fields['victim.contact'] = new_vic_contact

    new_vic_address = request.form.get('vic_address')
    if new_vic_address and new_vic_address != victim.get('address'):
        updated_fields['victim.address'] = new_vic_address

    suspect_list = case.get('suspect', [{}])
    suspect = suspect_list[0] if suspect_list else {}

    def set_suspect_field(field):
        val = request.form.get(f'sus_{field}')
        if val and val != suspect.get(field):
            updated_fields[f'suspect.0.{field}'] = val

    set_suspect_field('name')
    set_suspect_field('contact')
    set_suspect_field('email')
    set_suspect_field('status')
    set_suspect_field('address')

    if updated_fields:
        current_app.db.cases.update_one({"_id": ObjectId(case_id)}, {"$set": updated_fields})
        flash("Case updated successfully.", "success")
    else:
        flash("No changes detected.", "info")

    return redirect(url_for('cases.view_case', case_id=case_id))


@case_bp.route('/api/<case_id>', methods=['GET'])
@login_required
def get_case(case_id):
    try:
        if not ObjectId.is_valid(case_id):
            return jsonify({'error': 'Invalid case ID format'}), 400

        case = current_app.db.cases.find_one({'_id': ObjectId(case_id)})
        if not case:
            return jsonify({'error': 'Case not found'}), 404

        if session.get('role') != 'Admin' and str(case.get('officer_id')) != str(session.get('user_id')):
            return jsonify({'error': 'Unauthorized'}), 403

        officer = current_app.db.officers.find_one({'_id': ObjectId(case.get('officer_id'))})
        officer_name = officer['off_name'] if officer else 'Unknown'

        response_data = {
            'case': {
                'id': str(case['_id']),
                'case_number': case.get('case_number'),
                'case_title': case.get('case_title'),
                'status': case.get('status'),
                'officer_id': case.get('officer_id'),
                'officer_name': officer_name,
                'description': case.get('description', ''),
                'notes': case.get('notes', ''),
                'created_at': case.get('created_at').isoformat() if case.get('created_at') else None,
                'evidence_ids': case.get('evidence_ids', []),
                'suspect_ids': case.get('suspect_ids', [])
            }
        }
        return jsonify(response_data)

    except Exception as e:
        current_app.logger.error(f"Error fetching case {case_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
