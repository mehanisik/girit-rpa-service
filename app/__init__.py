from flask import Flask, jsonify
from core.config import settings
from .extensions import db, migrate, ma, cors
from .celery_app import celery, init_celery


def create_app(config_object=settings):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(
        app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", [])}}
    )

    if not app.config.get("TESTING", False):
        init_celery(app, celery)

    from .routes.health import health_bp
    from .routes.bots import bots_bp
    from .routes.jobs import jobs_bp

    app.register_blueprint(health_bp, url_prefix=f"{settings.API_V1_STR}/health")
    app.register_blueprint(bots_bp, url_prefix=f"{settings.API_V1_STR}/bots")
    app.register_blueprint(jobs_bp, url_prefix=f"{settings.API_V1_STR}/jobs")

    @app.route("/")
    def index():
        return jsonify(
            message=f"Welcome to {settings.PROJECT_NAME}! API is at {settings.API_V1_STR}"
        )

    with app.app_context():
        from . import tasks

    return app
