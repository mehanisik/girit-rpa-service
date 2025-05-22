from flask import Flask, jsonify
from core.config import settings
from .extensions import db, migrate, ma, cors

def create_app(config_object=settings):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", [])}})

    from .routes.health import health_bp
    from .routes.bots import bots_bp

    app.register_blueprint(health_bp, url_prefix=f"{settings.API_V1_STR}/health")
    app.register_blueprint(bots_bp, url_prefix=f"{settings.API_V1_STR}/bots")

    @app.route("/")
    def index():
        return jsonify(message=f"Welcome to {settings.PROJECT_NAME}! API is at {settings.API_V1_STR}")

    return app