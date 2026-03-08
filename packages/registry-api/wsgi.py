import os
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    import time
    with app.app_context():
        # 確保資料庫目錄存在 (僅針對 SQLite)
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
        if db_uri and db_uri.startswith("sqlite:///"):
            db_path = db_uri.replace("sqlite:///", "").replace("sqlite://", "")
            if db_path:
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
        
        # 嘗試建立資料表，若失敗則重試（針對 PostgreSQL 啟動較慢的情況）
        max_retries = 5
        for i in range(max_retries):
            try:
                db.create_all()
                print("Database synchronized successfully.")
                break
            except Exception as e:
                print(f"Database connection waiting... ({i+1}/{max_retries}): {e}")
                if i == max_retries - 1:
                    print("Could not connect to database, starting app anyway for debugging.")
                else:
                    time.sleep(3)
                    
    app.run(host="0.0.0.0", port=5006, debug=True)
