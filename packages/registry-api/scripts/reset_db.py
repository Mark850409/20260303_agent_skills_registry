import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Skill, SkillVersion, User

def reset():
    app = create_app('development')
    with app.app_context():
        # SQLite doesn't always drop everything cleanly with drop_all
        # So we manually delete the file if possible
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            # 處理 Windows 與 Unix 的路徑差異
            db_path = db_uri.replace('sqlite:///', '')
            # 針對 Windows 的絕對路徑（例如 sqlite:///C:\...）需要額外處理
            if os.name == 'nt' and db_path.startswith('/'):
                 db_path = db_path.lstrip('/')
            
            if os.path.exists(db_path):
                print(f"Deleting database file: {db_path}")
                try:
                    os.remove(db_path)
                except Exception as e:
                    print(f"Error removing file: {e}")

        
        print("Creating all tables...")
        db.create_all()
        print("DB Reset Complete")

if __name__ == "__main__":
    reset()
