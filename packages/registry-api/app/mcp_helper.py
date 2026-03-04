import json
import os
import subprocess
import time
import re
import httpx
import logging
import threading
from flask import current_app

logger = logging.getLogger(__name__)

def run_introspection_task(server_id, env_values=None):
    """啟動背景執行緒進行工具內省"""
    # 獲取 Flask App 實例以供執行緒使用
    from flask import current_app
    app = current_app._get_current_object()
    
    def _task():
        with app.app_context():
            from app.models import MCPServer
            from app import db
            
            server = MCPServer.query.get(server_id)
            if not server:
                return
            
            logger.info(f"Starting background introspection for MCP: {server.name}")
            introspection_data = {
                "transport": server.transport,
                "endpoint_url": server.endpoint_url,
                "local_config": server.local_config
            }
            try:
                tools = introspect_mcp_tools(introspection_data, env_overrides=env_values)
                if tools:
                    server.tools = tools
                    db.session.commit()
                    logger.info(f"Successfully introspected {len(tools)} tools for {server.name}")
                else:
                    logger.warning(f"No tools found during introspection for {server.name}")
            except Exception as e:
                logger.error(f"Introspection task failed for {server.name}: {e}")

    thread = threading.Thread(target=_task)
    thread.daemon = True
    thread.start()

def introspect_mcp_tools(server_data, env_overrides=None):
    """
    主要進入點：根據傳輸方式嘗試擷取工具清單。
    """
    transport = server_data.get("transport", "sse")
    
    if transport == "sse":
        url = server_data.get("endpoint_url")
        if url:
            tools = introspect_sse_tools(url.strip()) # Modified line
            return tools # Added return statement
    
    elif transport == "stdio":
        local_configs = server_data.get("local_config", [])
        if local_configs:
            # 優先嘗試第一個配置
            lc = local_configs[0].copy()
            if env_overrides:
                # 合併傳入的環境變數覆蓋
                existing_envs = lc.get("env_values", {})
                existing_envs.update(env_overrides)
                lc["env_values"] = existing_envs
            return introspect_stdio_tools(lc)
            
    return []

def introspect_sse_tools(url):
    """透過 HTTP 向遠端 SSE 端點請求工具清單"""
    url = url.strip()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
def introspect_sse_tools(url):
    """透過 HTTP 向遠端 SSE 端點請求工具清單 (完整 MCP 初始化流程)"""
    url = url.strip()
    init_payload = {
        "jsonrpc": "2.0", 
        "id": 0, 
        "method": "initialize", 
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "registry-api-introspector", "version": "1.0.0"}
        }
    }
    tools_payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    
    start_t = time.time()
    try:
        logger.info(f"SSE Full Handshake & Session at {url}...")
        # 必須保持 GET 連線，因為回應會透過串流送回
        with httpx.stream("GET", url, timeout=15, headers={"Accept": "text/event-stream"}) as response:
            if response.status_code != 200:
                logger.error(f"SSE GET failed with status {response.status_code}")
                return []

            mcp_endpoint = None
            initialized = False
            
            for line in response.iter_lines():
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    
                    # 階段 1: 取得 Endpoint 並發送 initialize
                    if not mcp_endpoint:
                        from urllib.parse import urljoin
                        mcp_endpoint = urljoin(url, data_str)
                        logger.info(f"Found MCP endpoint: {mcp_endpoint}. Sending 'initialize'...")
                        try:
                            httpx.post(mcp_endpoint, json=init_payload, timeout=5)
                        except Exception as e:
                            logger.error(f"Failed to send initialize to SSE: {e}")
                            break
                        continue
                    
                    # 階段 2: 處理 JSON-RPC 回應
                    try:
                        resp_json = json.loads(data_str)
                        msg_id = resp_json.get("id")
                        
                        # 處理 initialize 回應 -> 發送 tools/list
                        if msg_id == 0 and not initialized:
                            logger.info("Received 'initialize' response. Sending 'tools/list'...")
                            initialized = True
                            # 發送 initialized 通知 (標準協定推薦)
                            try:
                                httpx.post(mcp_endpoint, json={"jsonrpc": "2.0", "method": "notifications/initialized"}, timeout=2)
                                # 請求工具
                                httpx.post(mcp_endpoint, json=tools_payload, timeout=5)
                            except Exception as e:
                                logger.error(f"Failed to send follow-up requests to SSE: {e}")
                                break
                        
                        # 處理 tools/list 回應 -> 回傳結果
                        elif msg_id == 1:
                            tools = resp_json.get("result", {}).get("tools", [])
                            logger.info(f"Successfully introspected {len(tools)} tools via SSE session")
                            return tools
                            
                    except json.JSONDecodeError:
                        continue

                # 總體 20 秒超時保護
                if time.time() - start_t > 20:
                    logger.warning("SSE full introspection timed out")
                    break
    except Exception as e:
        logger.error(f"SSE full introspection failed for {url}: {e}")
        
    return []

def introspect_stdio_tools(lc):
    """啟動本地 stdio MCP 並取得工具清單"""
    t = lc.get("type")
    cmd = lc.get("command", "")
    pkg = lc.get("package", "")
    
    # 指令優化 (比照 CLI)
    cmd = cmd.strip()
    pkg = (pkg or "").strip()
    
    # 環境變數標籤 (用於 Docker)
    env_flags = ""
    if t == "docker":
        env_vals = lc.get("env_values", {})
        for k in lc.get("env", []):
            if k in env_vals:
                env_flags += f' -e {k}="{env_vals[k]}"'

    if t == "node" and pkg and "npx" in cmd and pkg not in cmd:
        real_command = f"{cmd} -y {pkg}"
    elif t == "python" and pkg and "python" in cmd and pkg not in cmd:
        # 如果 pkg 看起來像是一個路徑或檔名
        if pkg.endswith(".py") or "/" in pkg or "\\" in pkg:
            real_command = f"{cmd} {pkg}"
        else:
            real_command = f"{cmd} -m {pkg}"
    elif t == "docker":
        if env_flags and "docker run" in cmd:
            real_command = cmd.replace("docker run", f"docker run{env_flags}")
        else:
            real_command = f"{cmd} {pkg}".strip()
    else:
        real_command = f"{cmd} {pkg}".strip()
    
    # 合併環境變數
    env = os.environ.copy()
    env_values = lc.get("env_values", {})
    if env_values:
        for k, v in env_values.items():
            env[k] = str(v)
            
    try:
        proc = subprocess.Popen(
            real_command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            bufsize=0
        )
    except FileNotFoundError:
        logger.error(f"Executable not found for command: {real_command}. If running in Docker, ensure the runtime (Node/Python/Docker) is installed in the container.")
        return []
    except Exception as e:
        logger.error(f"Failed to start subprocess: {e}")
        return []

    tools = []
    try:
        # 1. Initialize
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "registry-backend", "version": "1.0.0"}
            }
        }) + "\n")
        
        def find_json(line):
            match = re.search(r'\{.*"jsonrpc".*\}', line)
            if match:
                try: return json.loads(match.group())
                except: return None
            return None

        init_ok = False
        start_time = time.time()
        
        while time.time() - start_time < 15:
            if proc.poll() is not None: break
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            logger.debug(f"[Introspect] Received: {line.strip()}")
            data = find_json(line)
            if data and data.get("id") == 1:
                init_ok = True
                logger.info(f"Initialize OK for {real_command}")
                break
        
        if init_ok:
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "method": "notifications/initialized"
            }) + "\n")
            
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
            }) + "\n")
            
            while time.time() - start_time < 20:
                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None: break
                    time.sleep(0.1)
                    continue
                
                logger.debug(f"[Introspect] Received Tools: {line.strip()}")
                data = find_json(line)
                if data and data.get("id") == 2:
                    tools = data.get("result", {}).get("tools", [])
                    logger.info(f"Successfully listed {len(tools)} tools")
                    break
        else:
            # 偵測失敗，嘗試讀取 stderr
            stderr_out = proc.stderr.read()
            if stderr_out:
                logger.error(f"Introspection failed. Stderr: {stderr_out}")
            else:
                logger.error("Introspection failed (no stderr, maybe timeout)")
    except Exception as e:
        logger.error(f"Error during stdio introspection: {e}")
    finally:
        proc.terminate()
        try: proc.wait(timeout=1)
        except: proc.kill()
        
    return tools
