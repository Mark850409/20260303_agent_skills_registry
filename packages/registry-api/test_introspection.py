from app.mcp_helper import introspect_mcp_tools, introspect_stdio_tools
import os
import sys

# 把當前目錄加入 path 以便 import app
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import MCPServer

app = create_app("development")

def test_n8n():
    with app.app_context():
        server = MCPServer.query.filter_by(name='n8n-mcp').first()
        if not server:
            print("Server n8n-mcp not found in DB.")
            return
            
        print(f"Server found: {server.name}")
        print(f"Transport: {server.transport}")
        print(f"Local Config: {server.local_config}")
        
        if server.local_config:
            lc = server.local_config[0]
            print("\nTesting stdio introspection...")
            tools = introspect_stdio_tools(lc)
            print(f"Detected Tools: {tools}")
            
            if tools:
                server.tools = tools
                db.session.commit()
                print("Successfully updated tools in DB.")
            else:
                print("Failed to detect tools.")

if __name__ == "__main__":
    test_n8n()
