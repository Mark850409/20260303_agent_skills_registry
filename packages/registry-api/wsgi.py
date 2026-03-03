import os
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    with app.app_context():
        # 確保資料庫目錄存在
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
        if db_uri and db_uri.startswith("sqlite:///"):
            db_path = db_uri.replace("sqlite:///", "").replace("sqlite://", "")
            if db_path:
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
