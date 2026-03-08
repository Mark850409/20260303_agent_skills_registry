import json
import os
import subprocess
import time
import re
import sys

# 把當前目錄加入 path 以便 import app
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import MCPServer

app = create_app("development")

def find_json(line):
    match = re.search(r'\{.*"jsonrpc".*\}', line)
    if match:
        try: return json.loads(match.group())
        except: return None
    return None

def introspect_stdio_tools_v2(local_config):
    """更魯棒的 Stdio 偵測版本"""
    m_type = local_config.get("type")
    command = local_config.get("command")
    pkg = local_config.get("package")
    env_list = local_config.get("env", [])
    
    args = []
    if m_type == "node":
        command = "npx"
        args = ["-y", pkg]
    elif m_type == "python":
        command = "python"
        pkg_name = pkg.replace("-", "_").split("/")[-1]
        args = ["-m", pkg_name]
    elif m_type == "docker":
        command = "docker"
        args = ["run", "-i", "--rm", pkg]

    real_command = [command] + args
    cmd_str = " ".join(real_command)
    print(f"Executing: {cmd_str}")
    
    env = os.environ.copy()
    # 這裡可以注入一些預設的環境變數，如果需要的話
    
    try:
        # 在 Windows 上使用 shell=True 處理 .cmd 檔案
        is_windows = os.name == 'nt'
        proc = subprocess.Popen(
            cmd_str if is_windows else real_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=is_windows,
            env=env,
            bufsize=1
        )
        
        # 1. Initialize
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "fix-script", "version": "1.0.0"}
            }
        }) + "\n")
        proc.stdin.flush()
        
        init_ok = False
        start_time = time.time()
        while time.time() - start_time < 10:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None: break
                time.sleep(0.1)
                continue
            print(f"Out: {line.strip()}")
            data = find_json(line)
            if data and data.get("id") == 1:
                init_ok = True
                break
        
        if init_ok:
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "method": "notifications/initialized"
            }) + "\n")
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
            }) + "\n")
            proc.stdin.flush()
            
            while time.time() - start_time < 20:
                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None: break
                    time.sleep(0.1)
                    continue
                data = find_json(line)
                if data and data.get("id") == 2:
                    tools = data.get("result", {}).get("tools", [])
                    return tools
        else:
            stderr_out = proc.stderr.read()
            print(f"Init failed. Stderr: {stderr_out}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'proc' in locals():
            proc.terminate()
            try: proc.wait(timeout=1)
            except: proc.kill()
    return []

def run_fix():
    with app.app_context():
        server = MCPServer.query.filter_by(name='n8n-mcp').first()
        if not server:
            print("n8n-mcp not found.")
            return
            
        if not server.local_config:
            print("No local_config found.")
            return
            
        tools = introspect_stdio_tools_v2(server.local_config[0])
        if tools:
            server.tools = tools
            db.session.commit()
            print(f"Successfully fixed n8n-mcp with {len(tools)} tools.")
        else:
            print("Failed to detect tools for n8n-mcp.")

if __name__ == "__main__":
    run_fix()
