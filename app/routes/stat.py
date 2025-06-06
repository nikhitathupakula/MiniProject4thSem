from flask import Blueprint, jsonify, render_template, current_app as app
from datetime import datetime
from bson import ObjectId, json_util

stats_bp = Blueprint('statistics', __name__, template_folder='templates')


@stats_bp.route('/dashboard.html/')
@stats_bp.route('/stats')
def show_stats():
    return render_template('statistics.html')

@stats_bp.route('/api/case-status')
def get_case_status():
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(app.db.cases.aggregate(pipeline))
    return jsonify(results)

@stats_bp.route('/api/investigator-load')
def get_investigator_load():
    pipeline = [
        {"$match": {"officer_id": {"$exists": True}}},
        {"$lookup": {
            "from": "officers",
            "localField": "officer_id",
            "foreignField": "_id",
            "as": "officer"
        }},
        {"$unwind": "$officer"},
        {"$group": {
            "_id": {
                "officer_id": {"$toString": "$officer_id"},
                "name": "$officer.off_name",
                "role": "$officer.role_name"
            },
            "case_count": {"$sum": 1}
        }},
        {"$sort": {"case_count": -1}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "officer_id": "$_id.officer_id",
            "name": "$_id.name",
            "role": "$_id.role",
            "case_count": 1
        }}
    ]
    results = list(app.db.cases.aggregate(pipeline))
    return json_util.dumps(results), 200, {'Content-Type': 'application/json'}

@stats_bp.route('/api/crime-trends')
def get_crime_trends():
    pipeline = [
        {
            "$project": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"}
            }
        },
        {
            "$group": {
                "_id": {"year": "$year", "month": "$month"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$limit": 12},
        {
            "$project": {
                "_id": 0,
                "year": "$_id.year",
                "month": "$_id.month",
                "count": 1,
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": 1
                            }
                        }
                    }
                }
            }
        }
    ]
    results = list(app.db.cases.aggregate(pipeline))
    return jsonify(results)

@stats_bp.route('/api/case-outcomes')
def get_case_outcomes():
    pipeline = [
        {"$match": {"officer_id": {"$exists": True}}},
        {"$lookup": {
            "from": "officers",
            "localField": "officer_id",
            "foreignField": "_id",
            "as": "officer"
        }},
        {"$unwind": "$officer"},
        {"$group": {
            "_id": {
                "off_name": "$officer.off_name",
                "status": "$status"
            },
            "count": {"$sum": 1}
        }},
        {"$group": {
            "_id": "$_id.off_name",
            "outcomes": {
                "$push": {
                    "status": "$_id.status",
                    "count": "$count"
                }
            },
            "total": {"$sum": "$count"}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "investigator": "$_id",
            "outcomes": 1,
            "total_cases": "$total"
        }}
    ]
    results = list(app.db.cases.aggregate(pipeline))
    return jsonify(results)
