import os
from app import create_app, db
from app.models import PromptKnowledge

def migrate():
    print("Initializing PromptKnowledge table...")
    app = create_app()
    with app.app_context():
        # Create all tables (this will add PromptKnowledge if it doesn't exist)
        db.create_all()
        print("PromptKnowledge table created successfully.")

if __name__ == "__main__":
    migrate()
