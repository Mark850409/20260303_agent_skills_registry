import sqlite3
import json
import os

db_path = os.path.join(os.getcwd(), 'data', 'registry.db')

def check_mcps():
    if not os.path.exists(db_path):
        # 嘗試上一層目錄
        db_path_alt = os.path.join(os.path.dirname(os.getcwd()), 'packages', 'registry-api', 'data', 'registry.db')
        if os.path.exists(db_path_alt):
            actual_db = db_path_alt
        else:
            print(f"DB not found at {db_path} or {db_path_alt}")
            return
    else:
        actual_db = db_path

    print(f"Connecting to {actual_db}...")
    conn = sqlite3.connect(actual_db)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, tools, local_config, created_at FROM mcp_servers ORDER BY created_at DESC LIMIT 5')
        rows = cursor.fetchall()
        
        print(f"{'ID':<4} | {'Name':<20} | {'Tools Count':<12} | {'Created At':<25}")
        print("-" * 75)
        
        for r in rows:
            m_id, name, tools_json, config_json, created_at = r
            tools = json.loads(tools_json) if tools_json else []
            config = json.loads(config_json) if config_json else []
            print(f"{m_id:<4} | {name:<20} | {len(tools):<12} | {created_at}")
            print(f"  Config: {json.dumps(config, indent=2)}")
            print("-" * 75)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_mcps()
