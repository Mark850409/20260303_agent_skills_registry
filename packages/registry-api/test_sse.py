
import httpx
import sys
import time

import json

def test_sse_introspection(url):
    print(f"--- Testing SSE Handshake (Full MCP Init) at: {url} ---")
    init_payload = {
        "jsonrpc": "2.0", 
        "id": 0, 
        "method": "initialize", 
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    tools_payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    
    try:
        start_t = time.time()
        with httpx.stream("GET", url, timeout=10, headers={"Accept": "text/event-stream"}) as response:
            print(f"GET Status: {response.status_code}")
            if response.status_code != 200:
                print("Failed to open SSE connection")
                return

            mcp_endpoint = None
            initialized = False
            
            for line in response.iter_lines():
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    
                    # 1. 取得 Endpoint 並發送 initialize
                    if not mcp_endpoint:
                        from urllib.parse import urljoin
                        mcp_endpoint = urljoin(url, data_str)
                        print(f"  >>> Found Endpoint: {mcp_endpoint}")
                        print(f"  >>> Sending 'initialize' request...")
                        httpx.post(mcp_endpoint, json=init_payload, timeout=5)
                        continue
                    
                    # 2. 解析 SSE 回傳的 JSON (可能是 initialize 的回傳，也可能是 tools/list 的回傳)
                    try:
                        resp_json = json.loads(data_str)
                        msg_id = resp_json.get("id")
                        
                        # 處理 initialize 回應
                        if msg_id == 0:
                            print(f"  >>> Received 'initialize' response! Sending 'tools/list'...")
                            initialized = True
                            # 發送 initialized 通知 (選配但推薦)
                            init_notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
                            httpx.post(mcp_endpoint, json=init_notif, timeout=2)
                            # 發送真正的工具請求
                            httpx.post(mcp_endpoint, json=tools_payload, timeout=5)
                        
                        # 處理 tools/list 回應
                        elif msg_id == 1:
                            tools = resp_json.get("result", {}).get("tools", [])
                            print(f"\nSUCCESS! Found {len(tools)} tools via SSE stream:")
                            for t in tools:
                                print(f" - {t.get('name')}: {t.get('description')}")
                            return
                            
                    except json.JSONDecodeError:
                        continue

                if time.time() - start_t > 20:
                    print("Timeout waiting for sequence to complete")
                    break
    except Exception as e:
        print(f"SSE Session Error: {e}")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://host.docker.internal:8003/sse"
    test_sse_introspection(url)
