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
    
    migrate.init_app(app, db)

    migrate.init_app(app, db)
    CORS(app, origins="*")

    from flask_smorest import Api
    api = Api(app)

    # Register blueprints (using flask-smorest)
    from app.routes.skills import skills_blp
    from app.routes.auth import auth_blp
    from app.routes.admin import admin_blp
    from app.routes.mcps import mcps_blp
    from app.routes.prompts import bp as prompts_blp
    from app.routes.admin_prompts import bp as admin_prompts_blp
    from app.routes.admin_prompts import public_bp as public_prompts_blp

    from app.routes.prompt_knowledge import admin_knowledge_bp, public_knowledge_bp
    from app.routes.docker import docker_bp
    from app.routes.npm import npm_bp
    
    api.register_blueprint(skills_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(admin_blp)
    api.register_blueprint(mcps_blp)
    api.register_blueprint(prompts_blp)
    api.register_blueprint(admin_prompts_blp)
    api.register_blueprint(admin_knowledge_bp)
    
    app.register_blueprint(public_prompts_blp)
    app.register_blueprint(public_knowledge_bp)
    app.register_blueprint(docker_bp, url_prefix='/api/docker')
    app.register_blueprint(npm_bp, url_prefix='/api/npm')

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app
