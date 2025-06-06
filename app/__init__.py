from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
from flask_htmx import HTMX
from bson import ObjectId
from bson.dbref import DBRef

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login_page"

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
    app.config['WTF_CSRF_ENABLED'] = False
    htmx = HTMX(app)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    app.config["SESSION_PROTECTION"] = "strong"

    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    app.db = client["test"]

    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    @app.template_filter('tojson_safe')
    def tojson_safe(value, **kwargs):
        def convert(o):
            if isinstance(o, ObjectId):
                return str(o)
            elif isinstance(o, datetime):
                return o.isoformat()
            elif isinstance(o, DBRef):
                return str(o)
            raise TypeError
        import json
        return json.dumps(value, default=convert, **kwargs)

    from app.routes.auth_routes import auth_bp
    from app.routes.dash_route import dashboard_bp
    from app.routes.case_route import case_bp
    from app.routes.evidence_route import evidence_bp
    from app.routes.laws_route import laws_bp
    from app.routes.employee_route import employee_bp
    from app.routes.sus_route import sus_bp
    from app.routes.stat import stats_bp
    app.register_blueprint(case_bp)
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(evidence_bp, url_prefix="/dashboard")
    app.register_blueprint(laws_bp, url_prefix="/dashboard")
    app.register_blueprint(employee_bp, url_prefix="/dashboard")
    app.register_blueprint(sus_bp, url_prefix="/dashboard")
    app.register_blueprint(stats_bp, url_prefix="/stats")

    return app
