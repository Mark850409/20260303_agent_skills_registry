from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins="*")

    # Register blueprints
    from app.routes.skills import skills_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(skills_bp, url_prefix="/api/skills")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app
