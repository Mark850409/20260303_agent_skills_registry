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

    from flask_smorest import Api
    api = Api(app)

    # Register blueprints (using flask-smorest)
    from app.routes.skills import skills_blp
    from app.routes.auth import auth_blp
    from app.routes.admin import admin_blp

    api.register_blueprint(skills_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(admin_blp)

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app
