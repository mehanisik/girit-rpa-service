from flask import Blueprint, jsonify
from app.extensions import db 
from sqlalchemy import text
from core.config import settings

health_bp = Blueprint("health", __name__)

@health_bp.route("/", methods=["GET"])
def health_check():
    db_status = "disconnected"
    db_error = None
    try:
        result = db.session.execute(text("SELECT 1")).scalar_one()
        if result == 1:
            db_status = "connected"
    except Exception as e:
        db_error = str(e)
        db.session.rollback()
        db_status = "error"
        print(f"Health check DB error: {e}")

    response = {
        "status": "healthy" if db_status == "connected" else "degraded",
        "project_name": settings.PROJECT_NAME,
        "database_status": db_status
    }
    if db_error:
        response["database_error"] = db_error

    status_code = 200 if db_status == "connected" else 503
    return jsonify(response), status_code