from flask import render_template, Blueprint
from app.models import get_all_laws

laws_bp = Blueprint('laws', __name__, url_prefix='/dashboard')

@laws_bp.route('/laws')
def laws():
    try:
        laws_data = get_all_laws()
    except Exception as e:
        return f"An error occurred while fetching the laws data: {str(e)}", 500

    return render_template('laws.html', laws=laws_data)
