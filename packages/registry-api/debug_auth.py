import sqlite3
import hashlib
import os

db_path = 'e:/Project/AI/AgentSkills/20260303_agent_skills_registry/packages/registry-api/data/registry.db'

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def check():
    if not os.path.exists(db_path):
        print("DB not found")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, username, api_token_hash, role FROM users")
    users = c.fetchall()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"ID: {u[0]}, User: {u[1]}, Role: {u[3]}, Hash starts: {u[2][:8] if u[2] else 'None'}")
    
    conn.close()

if __name__ == "__main__":
    check()
