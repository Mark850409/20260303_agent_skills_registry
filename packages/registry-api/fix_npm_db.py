import os
from app import create_app, db
from app.models import NpmPackage

app = create_app(os.environ.get("FLASK_ENV", "development"))
with app.app_context():
    pkgs = NpmPackage.query.all()
    count = 0
    for p in pkgs:
        if p.name != 'agentskills':
            db.session.delete(p)
            count += 1
    db.session.commit()
    print(f"Deleted {count} external packages from the database.")
