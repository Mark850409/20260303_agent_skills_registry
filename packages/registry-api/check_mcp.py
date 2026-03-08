import sqlite3
import json
import os

db_path = 'e:/Project/AI/AgentSkills/20260303_agent_skills_registry/packages/registry-api/data/registry.db'

def check():
    if not os.path.exists(db_path):
        print("DB not found")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name, transport, local_config, tools FROM mcp_servers WHERE name IN ('aaa', 'filesystem')")
    rows = c.fetchall()
    
    for row in rows:
        name, transport, local_config, tools = row
        print(f"Server: {name}")
        print(f"Transport: {transport}")
        
        lc = json.loads(local_config) if local_config else []
        print(f"Local Config: {json.dumps(lc, indent=2)}")
        
        t = json.loads(tools) if tools else []
        print(f"Tools Count: {len(t)}")
        print("-" * 20)
    
    conn.close()

if __name__ == "__main__":
    check()
