import os
import sys
import json
import logging

# 設定日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 將當前目錄加入 PATH
sys.path.append(os.getcwd())

from app.mcp_helper import introspect_mcp_tools

def debug_firecrawl():
    # 模擬從 GUI 傳來的資料
    local_config = [
        {
            "type": "node",
            "command": "npx",
            "package": "firecrawl-mcp",
            "env": ["FIRECRAWL_API_KEY"]
        }
    ]
    
    # 使用者在介面輸入的值
    env_overrides = {
        "FIRECRAWL_API_KEY": "fc-9c9269fbc0054cd7b05e7d1541e3b767"
    }
    
    server_data = {
        "transport": "stdio",
        "local_config": local_config
    }
    
    print("=== Starting Debug Introspection ===")
    tools = introspect_mcp_tools(server_data, env_overrides=env_overrides)
    
    print("\n=== Result ===")
    print(f"Detected Tools: {len(tools)}")
    if tools:
        for t in tools[:3]:
            print(f" - {t.get('name')}: {t.get('description')[:50]}...")
    else:
        print("Failed to detect tools.")

if __name__ == "__main__":
    debug_firecrawl()
