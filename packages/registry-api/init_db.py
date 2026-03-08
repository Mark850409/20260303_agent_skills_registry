import os
import sys

# 將 app 目錄加入路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def init_admin(password="admin123"):
    app = create_app("development")
    with app.app_context():
        # 自動建立所有資料表 (如果不存在)
        print("Creating table schema if not exists...")
        db.create_all()
        
        # 檢查管理員是否存在
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin",
                email="admin@example.com",
                role="admin",
                permissions=["*:*"]
            )
            db.session.add(admin)
        
        print(f"Setting password for admin...")
        admin.password_hash = generate_password_hash(password)
        db.session.commit()
        print("Admin user initialized successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--password", default="admin123", help="Initial admin password")
    args = parser.parse_args()
    init_admin(args.password)
