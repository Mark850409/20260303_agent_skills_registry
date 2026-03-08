import sqlite3
import os

db_path = 'e:/Project/AI/AgentSkills/20260303_agent_skills_registry/packages/registry-api/data/registry.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("--- Users ---")
    c.execute("SELECT id, username, role, api_token_hash FROM users")
    for row in c.fetchall():
        print(row)
        
    print("\n--- MCP Servers (n8n-mcp) ---")
    c.execute("SELECT name, transport, tools FROM mcp_servers WHERE name='n8n-mcp'")
    for row in c.fetchall():
        print(row)
    
    conn.close()
