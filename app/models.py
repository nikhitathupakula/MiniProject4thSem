from flask import current_app
from flask_login import UserMixin
from bson import ObjectId
import bcrypt

class User(UserMixin):
    def __init__(self, _id, off_name, role_name, hashed_pass):
        self.id = str(_id)
        self.username = off_name
        self.off_name = off_name
        self.role = role_name
        self.password_hash = hashed_pass

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @staticmethod
    def get(user_id):
        user_data = current_app.db["officers"].find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(
                user_data["_id"],
                user_data["off_name"],
                user_data["role_name"],
                user_data["hashed_pass"]
            )
        return None

    @staticmethod
    def get_by_username(username):
        user_data = current_app.db["officers"].find_one({"email": username})
        if user_data:
            return User(
                user_data["_id"],
                user_data["off_name"],
                user_data["role_name"],
                user_data["hashed_pass"]
            )
        return None

def get_evidence_by_id(evidence_id):
    return current_app.db["evidences"].find_one({"_id": ObjectId(evidence_id)})

def get_all_evidence():
    try:
        evidence_cursor = current_app.db.evidences.find()
        evidence_list = list(evidence_cursor)
        return evidence_list
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


def insert_evidence(evidence_data):
    return current_app.db["evidences"].insert_one(evidence_data)

def update_evidence(evidence_id, updated_data):
    return current_app.db["evidences"].update_one(
        {"_id": ObjectId(evidence_id)},
        {"$set": updated_data}
    )
    
def get_all_laws():
    return current_app.db.laws.find()

def add_evidence(new_evidence):
    try:
        result = current_app.db["evidences"].insert_one(new_evidence)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error adding evidence: {str(e)}")
