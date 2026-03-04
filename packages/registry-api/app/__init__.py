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

    # 啟用 ProxyFix 支援 HTTPS 和 Reverse Proxy
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Extensions
    db.init_app(app)
    
    # Enable SQLite WAL mode (Write-Ahead Logging) to improve concurrency
    with app.app_context():
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            from sqlalchemy import event
            @event.listens_for(db.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()

    migrate.init_app(app, db)
    CORS(app, origins="*")

    from flask_smorest import Api
    api = Api(app)

    # Register blueprints (using flask-smorest)
    from app.routes.skills import skills_blp
    from app.routes.auth import auth_blp
    from app.routes.admin import admin_blp
    from app.routes.mcps import mcps_blp

    api.register_blueprint(skills_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(admin_blp)
    api.register_blueprint(mcps_blp)

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app
