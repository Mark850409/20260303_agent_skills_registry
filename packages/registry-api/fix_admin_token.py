import sqlite3
import hashlib
import os

db_path = 'e:/Project/AI/AgentSkills/20260303_agent_skills_registry/packages/registry-api/data/registry.db'
token = "admin-token-123"
token_hash = hashlib.sha256(token.encode()).hexdigest()

def fix():
    if not os.path.exists(db_path):
        print("DB not found")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Update admin token hash
    c.execute("UPDATE users SET api_token_hash = ? WHERE username = 'admin'", (token_hash,))
    if c.rowcount > 0:
        print(f"Successfully updated admin token hash to: {token_hash}")
    else:
        print("Admin user not found in DB.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix()
