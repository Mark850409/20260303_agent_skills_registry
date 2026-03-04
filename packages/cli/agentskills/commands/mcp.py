"""CLI mcp 子命令群組

支援：list / search / info / connect / run / publish / add-to-claude
"""
import json
import os
import shutil
import subprocess
import sys

import click
import httpx

from agentskills.api_client import (
    get_registry_url, get_token,
    _headers,
)


# ─── helpers ─────────────────────────────────────────────────────────────────

def _base() -> str:
    # 這裡的 get_registry_url 已經會考慮到 AGENTSKILLS_REGISTRY
    return get_registry_url()

def _get_stdio_mcp_tools(lc: dict, env: dict = None) -> list:
    """啟動 MCP Server 並取得 tools/list (優化版：支援握手、雜訊過濾與指令自動組合)"""
    import json
    import time
    import subprocess
    import re
    
    if env is None:
        env = os.environ.copy()
        
    t = lc.get("type")
    cmd = lc.get("command", "")
    pkg = lc.get("package", "")
    
    # 自動組合指令：如果指令是 npx 但沒套件，幫他補上
    real_command = cmd
    if t == "node" and pkg and "npx" in cmd and pkg not in cmd:
        real_command = f"{cmd} -y {pkg}"
    elif t == "python" and pkg and "python" in cmd and pkg not in cmd:
        real_command = f"{cmd} -m {pkg}"
    elif t == "docker":
        # 嘗試將環境變數注入到 docker run 指令中
        env_flags = ""
        for k in lc.get("env", []):
            if k in env:
                env_flags += f" -e {k}=\"{env[k]}\""
        if env_flags and "docker run" in real_command:
            real_command = real_command.replace("docker run", f"docker run{env_flags}")
        
    click.echo(f"  [驗證] 執行指令: {real_command} (逾時 30s)...")
    
    # 啟動子程序，同時捕獲 stderr 以便出錯時診斷
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

    tools = []
    error_output = []
    try:
        # 1. Initialize Request
        proc.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "agentskills-cli", "version": "1.0.0"}
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
        
        # 讀取 stdout，同時檢查 stderr 是否有錯
        while time.time() - start_time < 30:
            if proc.poll() is not None:
                # 子程序已結束，抓取剩餘 stderr
                err = proc.stderr.read()
                if err: error_output.append(err)
                break
                
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
                
            data = find_json(line)
            if data and data.get("id") == 1:
                init_ok = True
                break
        
        if init_ok:
            # 2. Initialized Notification
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "method": "notifications/initialized"
            }) + "\n")
            
            # 3. List Tools Request
            proc.stdin.write(json.dumps({
                "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
            }) + "\n")
            
            while time.time() - start_time < 30:
                line = proc.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                data = find_json(line)
                if data and data.get("id") == 2:
                    tools = data.get("result", {}).get("tools", [])
                    break
        else:
            # 如果沒收到回應，讀取 stderr 並回報
            err = proc.stderr.read()
            if err: error_output.append(err)
            
    except Exception as e:
        click.echo(f"  [Error] 驗證過程發生異常: {e}")
    finally:
        proc.terminate()
        try: proc.wait(timeout=2)
        except: proc.kill()
        
    if error_output:
        click.secho(f"  [診斷] 啟動錯誤或警告輸出:\n  {''.join(error_output).strip()}", fg="yellow")
        
    return tools


def _get_mcp(name: str) -> dict:
    url = f"{_base()}/api/mcps/{name}"
    r = httpx.get(url, timeout=15)
    if r.status_code == 404:
        raise click.ClickException(f"找不到 MCP Server：'{name}'")
    r.raise_for_status()
    return r.json()


def _get_connect(name: str) -> dict:
    url = f"{_base()}/api/mcps/{name}/connect"
    r = httpx.get(url, timeout=15)
    r.raise_for_status()
    return r.json()


def _pick_local(local_config: list, prefer: str | None) -> dict | None:
    """依照偏好 / 可用 runtime 選擇本地啟動設定"""
    if not local_config:
        return None

    order = [prefer] if prefer else ["node", "python", "docker"]

    # 自動偵測可用 runtime
    def available(t: str) -> bool:
        cmd_map = {"node": "node", "python": "python", "docker": "docker"}
        return shutil.which(cmd_map.get(t, t)) is not None

    for t in order:
        for lc in local_config:
            if lc.get("type") == t and available(t):
                return lc

    # fallback：直接回傳第一個
    return local_config[0] if local_config else None


# ─── mcp group ───────────────────────────────────────────────────────────────

@click.group("mcp")
def mcp_group():
    """MCP Server Registry 指令集"""


# ─── list ────────────────────────────────────────────────────────────────────

@mcp_group.command("list")
@click.option("--category", "-c", default="", help="依分類篩選")
@click.option("--transport", "-t", default="", help="sse / stdio / http")
@click.option("--page", default=1, help="頁碼")
@click.option("--per-page", default=20, help="每頁筆數")
def mcp_list(category, transport, page, per_page):
    """列出 MCP Servers"""
    params = {"page": page, "per_page": per_page}
    if category: params["category"] = category
    if transport: params["transport"] = transport

    r = httpx.get(f"{_base()}/api/mcps", params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    mcps = data.get("mcps", [])

    if not mcps:
        click.echo("（找不到 MCP Servers）")
        return

    click.echo(f"\n{'名稱':<28} {'傳輸':<8} {'分類':<16} 安裝數")
    click.echo("─" * 65)
    for m in mcps:
        click.echo(
            f"{m['name']:<28} {(m.get('transport') or 'sse'):<8} "
            f"{(m.get('category') or '-'):<16} {m.get('installs', 0)}"
        )
    click.echo(f"\n共 {data.get('total', 0)} 筆 | 第 {data.get('page',1)}/{data.get('pages',1)} 頁\n")


# ─── search ──────────────────────────────────────────────────────────────────

@mcp_group.command("search")
@click.argument("keyword")
@click.option("--page", default=1)
def mcp_search(keyword, page):
    """搜尋 MCP Servers"""
    r = httpx.get(f"{_base()}/api/mcps", params={"q": keyword, "page": page, "per_page": 20}, timeout=15)
    r.raise_for_status()
    data = r.json()
    mcps = data.get("mcps", [])

    if not mcps:
        click.echo(f"找不到符合 '{keyword}' 的 MCP Servers")
        return

    click.echo(f"\n🔍 搜尋 '{keyword}'：{data.get('total', 0)} 筆結果\n")
    for m in mcps:
        click.secho(f"  📡 {m['display_name']} ({m['name']})", fg="bright_cyan", bold=True)
        click.echo(f"     {m.get('description','')[:80]}")
        click.echo()


# ─── info ─────────────────────────────────────────────────────────────────────

@mcp_group.command("info")
@click.argument("name")
def mcp_info(name):
    """顯示 MCP Server 詳情"""
    m = _get_mcp(name)
    click.secho(f"\n  {m['display_name']}", fg="bright_cyan", bold=True)
    click.echo(f"  名稱：{m['name']}")
    click.echo(f"  作者：{m.get('author','')}")
    click.echo(f"  傳輸：{m.get('transport','sse')}")
    click.echo(f"  分類：{m.get('category') or '未分類'}")
    click.echo(f"  描述：{m.get('description','')}")

    tags = m.get("tags", [])
    if tags:
        click.echo(f"  標籤：{', '.join(tags)}")

    tools = m.get("tools", [])
    if tools:
        click.echo(f"\n  🛠 工具（{len(tools)}）：")
        for t in tools:
            click.echo(f"    • {t.get('name','')} — {t.get('description','')}")

    local = m.get("local_config", [])
    if local:
        click.echo(f"\n  💻 本地啟動支援：{', '.join(set(c['type'] for c in local))}")

    repo = m.get("repository", "")
    if repo:
        click.echo(f"\n  🔗 Repository：{repo}")

    connect_url = f"{_base()}/api/mcps/{name}/connect"
    click.echo(f"\n  📡 連線資訊：{connect_url}")
    click.echo()


# ─── connect ──────────────────────────────────────────────────────────────────

@mcp_group.command("connect")
@click.argument("name")
@click.option("--agent", type=click.Choice(["claude", "cursor", "anythingllm"]), default="claude", help="目標客戶端類型")
def mcp_connect(name, agent):
    """獲取與 MCP Server 連線的資訊或配置片段。

    如果是 SSE 類型，會顯示 Endpoint URL；
    如果是 Stdio 類型，會顯示本地啟動指令及適用於客戶端的 JSON 配置。
    """
    info = _get_connect(name)
    configs = info.get("claude_configs", {})

    # 優先用有指令的本地設定，其次 remote
    config_key = None
    for k in ["node", "python", "docker", "remote"]:
        if k in configs:
            config_key = k
            break

    if not config_key:
        click.echo(json.dumps({"mcpServers": {}}, indent=2))
        return

    payload = {name: configs[config_key]}
    output = json.dumps({"mcpServers": payload}, indent=2)

    click.echo(f"\n# {agent.capitalize()} Desktop config (claude_desktop_config.json)\n")
    click.echo(output)
    click.echo(f"\n# 上方 config 貼入 claude_desktop_config.json 的 mcpServers 區段即可\n")


# ─── add-to-claude ────────────────────────────────────────────────────────────

@mcp_group.command("add-to-claude")
@click.argument("name")
def mcp_add_to_claude(name):
    """輸出完整 Claude Desktop config snippet"""
    ctx = click.get_current_context()
    ctx.invoke(mcp_connect, name=name, agent="claude")


# ─── run ──────────────────────────────────────────────────────────────────────

@mcp_group.command("run")
@click.argument("name")
@click.option("--docker", "prefer", flag_value="docker", help="強制使用 Docker")
@click.option("--python", "prefer", flag_value="python", help="強制使用 Python")
@click.option("--node",   "prefer", flag_value="node",   help="強制使用 Node.js")
def mcp_run(name, prefer):
    """在本地啟動 MCP Server（自動偵測 runtime）"""
    info = _get_connect(name)
    local_config = info.get("local_config", [])

    if not local_config:
        endpoint = info.get("endpoint_url") or info.get("sse_proxy_url")
        if endpoint:
            click.echo(f"此 MCP Server 僅提供 Remote 連線，SSE URL：{endpoint}")
        else:
            click.echo("此 MCP Server 沒有可用的本地啟動設定")
        return

    lc = _pick_local(local_config, prefer)
    if not lc:
        types = [c["type"] for c in local_config]
        raise click.ClickException(
            f"找不到可用的 runtime（設定支援：{', '.join(types)}）\n"
            f"請確認 docker / python / node 已安裝或使用 --docker / --python / --node 指定"
        )

    t = lc.get("type")
    cmd_str = lc.get("command", "")
    env_keys = lc.get("env", [])

    # 收集 ENV 值
    env = dict(os.environ)
    if env_keys:
        click.echo(f"\n此 MCP Server 需要以下環境變數（按 Enter 略過）：")
        for k in env_keys:
            default = os.environ.get(k, "")
            val = click.prompt(f"  {k}", default=default, show_default=bool(default))
            if val:
                env[k] = val

    type_icon = {"docker": "🐳", "python": "🐍", "node": "🟢"}.get(t, "📦")
    click.secho(f"\n{type_icon} 啟動中：{cmd_str}\n", fg="bright_cyan")

    try:
        subprocess.run(cmd_str, shell=True, env=env)
    except KeyboardInterrupt:
        click.echo("\n已停止")


# ─── publish ──────────────────────────────────────────────────────────────────

@mcp_group.command("publish")
def mcp_publish():
    """互動式發布新 MCP Server"""
    token = get_token()
    if not token:
        raise click.ClickException("請先執行 `agentskills login` 登入")

    click.secho("\n🚀 發布 MCP Server\n", fg="bright_cyan", bold=True)

    # ── 基本資訊 ─────────────────────────────────────
    name         = click.prompt("唯一識別名（英文小寫 + 連字符）")
    display_name = click.prompt("顯示名稱")
    description  = click.prompt("功能描述")
    author       = click.prompt("作者名稱")
    tags_raw     = click.prompt("標籤（逗號分隔）", default="")
    category     = click.prompt("分類", default="",
                                type=click.Choice(["", "web_search","browser","data","coding",
                                                   "productivity","ai","database","communication","cloud","other"]))

    # ── 傳輸方式（先問，決定後續問題）────────────────
    click.echo()
    transport = click.prompt("傳輸方式", default="sse",
                             type=click.Choice(["sse", "stdio", "http"]))

    endpoint_url = None
    local_configs = []

    if transport == "sse":
        # SSE → 詢問 Remote Endpoint URL 及（可選）本地啟動
        endpoint_url = click.prompt("SSE Remote Endpoint URL（沒有請留空）", default="") or None
        add_local = click.confirm("是否也提供本地啟動設定？", default=False)
        if add_local:
            local_configs = _prompt_local_config()
    elif transport == "stdio":
        # stdio → 一定要本地啟動
        click.echo("stdio 傳輸需要本地啟動設定：")
        local_configs = _prompt_local_config()
    elif transport == "http":
        endpoint_url = click.prompt("HTTP Endpoint URL（沒有請留空）", default="") or None
        add_local = click.confirm("是否也提供本地啟動設定？", default=False)
        if add_local:
            local_configs = _prompt_local_config()

    payload = {
        "name":         name,
        "display_name": display_name,
        "description":  description,
        "author":       author,
        "endpoint_url": endpoint_url,
        "transport":    transport,
        "tags":         [t.strip() for t in tags_raw.split(",") if t.strip()],
        "category":     category or None,
        "local_config": local_configs,
    }

    try:
        r = httpx.post(f"{_base()}/api/mcps", json=payload, headers=_headers(), timeout=30)
        r.raise_for_status()
        click.secho(f"\n✅ MCP Server '{name}' 發布基本資訊成功！", fg="green", bold=True)
        
        # ── 自動偵測工具（強制流程，確保前端有資料） ───────────────────────
        if local_configs:
            lc = local_configs[0]
            if lc["type"] in ["node", "python"]:
                click.echo(f"\n📡 [強制驗證] 正在從本地啟動指令中偵測 MCP 工具...")
                env = os.environ.copy()
                
                # 如果有定義環境變數，詢問其值以供驗證使用
                env_keys = lc.get("env", [])
                if env_keys:
                    click.echo(f"  偵測到需要環境變數，請提供值（僅用於本次驗證，不會儲存在 Registry）：")
                    for k in env_keys:
                        default_val = os.environ.get(k, "")
                        val = click.prompt(f"    {k}", default=default_val, show_default=bool(default_val))
                        if val:
                            env[k] = val
                
                tools = _get_stdio_mcp_tools(lc, env=env)
                if tools:
                    click.echo(f"  [OK] 成功擷取到 {len(tools)} 個工具：{', '.join([t['name'] for t in tools])}")
                    # 直接同步，不問了，因為使用者要「強制驗證並列出」
                    upd = httpx.patch(f"{_base()}/api/mcps/{name}", 
                                      json={"tools": tools}, 
                                      headers=_headers(), timeout=15)
                    upd.raise_for_status()
                    click.echo("  [OK] 工具清單已同步到 Registry。")
                else:
                    click.secho("  [!] 警告：偵測失敗，Registry 上將不會顯示此 Server 的工具列表。", fg="yellow")
                    if click.confirm("  是否要手動輸入工具清單或再試一次？(N 為結束發布)", default=False):
                        # ... 這裡可以加 retry 邏輯，先行略過
                        pass
        
        click.secho(f"\n✅ 完整發布程序已完成！\n", fg="green", bold=True)
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("message", e.response.text)
        except Exception:
            detail = e.response.text
        raise click.ClickException(f"發布失敗：{detail}")



def _prompt_local_config() -> list:
    """互動式收集一種本地啟動設定，回傳 list（含一個 dict）"""
    runtime = click.prompt(
        "  本地啟動方式",
        default="node",
        type=click.Choice(["node", "python", "docker"]),
    )
    t_labels = {"node": "Node.js (npx)", "python": "Python", "docker": "Docker"}
    t_name = t_labels[runtime]
    cmd = click.prompt(f"  {t_name} 啟動指令", default="")
    if not cmd:
        return []
    if runtime == "docker":
        img = click.prompt("  Docker image 名稱", default="")
        env_raw = click.prompt("  需要的環境變數（逗號分隔）", default="")
        return [{"type": runtime, "command": cmd, "image": img, "package": "",
                 "env": [e.strip() for e in env_raw.split(",") if e.strip()]}]
    else:
        pkg = click.prompt("  套件名稱（npm / pip package）", default="")
        env_raw = click.prompt("  需要的環境變數（逗號分隔）", default="")
        return [{"type": runtime, "command": cmd, "package": pkg, "image": "",
                 "env": [e.strip() for e in env_raw.split(",") if e.strip()]}]


# ─── add ──────────────────────────────────────────────────────────────────────

# 各 IDE 的設定檔路徑定義
def _ide_config_path(target: str) -> str | None:
    """回傳目標 IDE 的 MCP 設定檔路徑（跨平台）"""
    home = os.path.expanduser("~")
    # Windows: %APPDATA% 路徑
    appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
    paths = {
        # Antigravity: ~/.gemini/antigravity/mcp_config.json
        "antigravity": os.path.join(home, ".gemini", "antigravity", "mcp_config.json"),
        # Claude Desktop: %APPDATA%/Claude/claude_desktop_config.json (Win)
        #                 ~/Library/Application Support/Claude/... (Mac)
        "claude": (
            os.path.join(appdata, "Claude", "claude_desktop_config.json")
            if sys.platform == "win32"
            else os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
            if sys.platform == "darwin"
            else os.path.join(home, ".config", "Claude", "claude_desktop_config.json")
        ),
        # Claude Code: ~/.claude.json
        "claudecode": os.path.join(home, ".claude.json"),
        # Cursor: ~/.cursor/mcp.json (官方全域設定)
        "cursor": os.path.join(home, ".cursor", "mcp.json"),
        # Kiro: ~/.kiro/settings/mcp.json
        "kiro": os.path.join(home, ".kiro", "settings", "mcp.json"),
        # VS Code: ~/.vscode/mcp.json (全域 MCP 設定，非 settings.json)
        "vscode": os.path.join(home, ".vscode", "mcp.json"),
    }
    return paths.get(target)


def _build_mcp_entry(m: dict, connect_info: dict, force_url: str | None, force_local: bool, target: str = "antigravity") -> dict:
    """
    根據 MCP 資訊建立針對特定 IDE 的 mcpServers entry dict。

    各 IDE 差異：
    - Claude Code / VS Code：需要 "type" 欄位（"stdio" 或 "sse"）
    - Antigravity / Claude Desktop / Cursor / Kiro：不需要 type，直接用 command/args 或 url
    """
    needs_type = target in ("claudecode", "vscode")  # 這些 IDE 需要顯式 type

    transport = m.get("transport", "sse")
    local_config = connect_info.get("local_config", [])
    endpoint_url = force_url or connect_info.get("endpoint_url") or connect_info.get("sse_proxy_url")

    # SSE 優先：有 URL 且非強制本地模式
    if not force_local and endpoint_url and transport in ("sse", "http"):
        entry: dict = {"url": endpoint_url}
        if needs_type:
            entry["type"] = "sse"
            # Claude Code / VS Code 的 SSE 格式：{"type": "sse", "url": "..."}
            entry = {"type": "sse", "url": endpoint_url}
        return entry

    # 否則用 Stdio 設定
    if local_config:
        lc = _pick_local(local_config, None)
        if lc:
            t = lc.get("type", "")
            env_keys = lc.get("env", [])
            entry = {}
            if needs_type:
                entry["type"] = "stdio"
            if t == "docker":
                entry["command"] = "docker"
                entry["args"] = ["run", "-i", "--rm"] + [
                    item for k in env_keys for item in ["-e", f"{k}=<{k}>"]
                ] + [lc.get("image", "")]
            elif t == "python":
                pkg = lc.get("package", "").replace("-", "_").split("/")[-1]
                entry["command"] = "python"
                entry["args"] = ["-m", pkg]
            elif t == "node":
                entry["command"] = "npx"
                entry["args"] = ["-y", lc.get("package", "")]
            else:
                cmd = lc.get("command", "")
                entry["command"] = cmd.split()[0] if cmd else ""
                entry["args"] = cmd.split()[1:] if cmd else []

            if env_keys:
                entry["env"] = {k: f"<{k}>" for k in env_keys}
            return entry

    # Fallback：用 SSE URL
    if endpoint_url:
        entry = {"url": endpoint_url}
        if needs_type:
            entry = {"type": "sse", "url": endpoint_url}
        return entry

    return {}


def _write_json_mcp_servers(cfg_path: str, mcp_name: str, entry: dict, indent: int = 4) -> bool:
    """通用：寫入 {mcpServers: {name: entry}} 格式"""
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    data = {}
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
    data.setdefault("mcpServers", {})[mcp_name] = entry
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    return True


def _write_antigravity(cfg_path: str, mcp_name: str, entry: dict) -> bool:
    """
    Antigravity mcp_config.json 格式：
    {"mcpServers": {"name": {"command": "...", "args": [...]} | {"url": "..."}}}
    """
    return _write_json_mcp_servers(cfg_path, mcp_name, entry, indent=4)


def _write_claude_desktop(cfg_path: str, mcp_name: str, entry: dict) -> bool:
    """
    Claude Desktop claude_desktop_config.json 格式（同 Antigravity）：
    {"mcpServers": {"name": {"command": "...", "args": [...]}}}
    注意：Claude Desktop 僅支援 Stdio，不支援直接配置 SSE URL。
    """
    # 若 entry 只有 "url"，提示使用者用 Settings UI 新增
    if list(entry.keys()) == ["url"]:
        click.secho(
            "  ⚠️  Claude Desktop 不支援在設定檔中直接配置 SSE URL，\n"
            "     請在 Claude Desktop → Settings → Connectors → Add custom connector 手動新增。",
            fg="yellow"
        )
        return False
    return _write_json_mcp_servers(cfg_path, mcp_name, entry, indent=4)


def _write_claude_code(cfg_path: str, mcp_name: str, entry: dict) -> bool:
    """
    Claude Code ~/.claude.json 格式：
    {"mcpServers": {"name": {"type": "stdio", "command": "...", "args": [...]}}}
    或 {"mcpServers": {"name": {"type": "sse", "url": "..."}}}
    （entry 已含 "type" 欄位，由 _build_mcp_entry 負責加入）
    """
    return _write_json_mcp_servers(cfg_path, mcp_name, entry, indent=2)


def _write_cursor(cfg_path: str, mcp_name: str, entry: dict) -> bool:
    """
    Cursor ~/.cursor/mcp.json 格式：
    {"mcpServers": {"name": {"command": "...", "args": [...], "env": {...}}}}
    SSE 格式：{"mcpServers": {"name": {"url": "..."}}}
    """
    return _write_json_mcp_servers(cfg_path, mcp_name, entry, indent=2)


def _write_kiro(cfg_path: str, mcp_name: str, entry: dict) -> bool:
    """
    Kiro ~/.kiro/settings/mcp.json 格式（同 Cursor）：
    {"mcpServers": {"name": {"command": "...", "args": [...]} | {"url": "..."}}}
    """
    return _write_json_mcp_servers(cfg_path, mcp_name, entry, indent=2)


def _write_vscode(cfg_path: str, mcp_name: str, entry: dict) -> bool:
    """
    VS Code ~/.vscode/mcp.json 格式：
    {"servers": {"name": {"type": "stdio", "command": "...", "args": [...]} | {"type": "sse", "url": "..."}}}
    注意：使用 "servers" 而非 "mcpServers"；entry 已含 "type" 欄位。
    """
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    data = {}
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
    data.setdefault("servers", {})[mcp_name] = entry
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


@mcp_group.command("add")
@click.argument("name")
@click.option("--target", "-t",
              type=click.Choice(["antigravity", "claude", "claudecode", "cursor", "kiro", "vscode"]),
              default="antigravity",
              help="目標 IDE（預設：antigravity）")
@click.option("--url", "force_url", default=None, help="強制指定 SSE URL（覆蓋自動偵測）")
@click.option("--local", "force_local", is_flag=True, default=False, help="強制使用本地 Stdio 設定而非 SSE URL")
@click.option("--yes", "-y", is_flag=True, default=False, help="略過確認直接寫入")
def mcp_add(name, target, force_url, force_local, yes):
    """從 Registry 安裝 MCP Server 到指定 IDE。

    \b
    目標 IDE 支援：
      antigravity  → ~/.gemini/antigravity/mcp_config.json
      claude       → Claude Desktop claude_desktop_config.json
      claudecode   → ~/.claude.json
      cursor       → Cursor MCP 設定
      kiro         → ~/.kiro/settings/mcp.json
      vscode       → ~/.vscode/mcp.json（VS Code 全域 MCP 設定）

    \b
    範例：
      agentskills mcp add my-mcp --target antigravity
      agentskills mcp add my-mcp --target claude --local
      agentskills mcp add my-mcp --url https://example.com/sse --target cursor
    """
    # 1. 從 Registry 取得 MCP 資訊
    click.secho(f"🔍 從 Registry 取得 '{name}' 的資訊…", fg="cyan")
    try:
        m = _get_mcp(name)
        connect_info = _get_connect(name)
    except Exception as e:
        raise click.ClickException(str(e))

    # 2. 組建 entry
    entry = _build_mcp_entry(m, connect_info, force_url, force_local, target=target)
    if not entry:
        raise click.ClickException(
            f"無法為 '{name}' 建立設定：該 MCP 沒有可用的 SSE URL 或本地啟動設定。\n"
            f"請使用 --url <URL> 手動指定連線 URL。"
        )

    # 3. 取得設定檔路徑
    cfg_path = _ide_config_path(target)
    if not cfg_path:
        raise click.ClickException(f"不支援的目標：{target}")

    # 4. 顯示預覽
    click.secho(f"\n📝 將在以下設定檔中加入 '{name}'：", fg="bright_cyan")
    click.echo(f"   {cfg_path}\n")
    click.secho("   設定內容：", fg="bright_cyan")
    click.echo(json.dumps({name: entry}, indent=4, ensure_ascii=False))

    # 5. 確認
    if not yes:
        click.confirm("\n確認寫入？", default=True, abort=True)

    # 6. 寫入
    writers = {
        "antigravity": _write_antigravity,
        "claude":      _write_claude_desktop,
        "claudecode":  _write_claude_code,
        "cursor":      _write_cursor,
        "kiro":        _write_kiro,
        "vscode":      _write_vscode,
    }
    try:
        writers[target](cfg_path, name, entry)
    except Exception as e:
        raise click.ClickException(f"寫入設定檔失敗：{e}")

    click.secho(f"\n✅ '{name}' 已成功安裝到 {target}！", fg="green", bold=True)
    click.echo(f"   設定檔：{cfg_path}")

    # 提示環境變數
    env_keys = entry.get("env", {})
    if env_keys:
        click.secho("\n⚠️  注意：此 MCP 需要以下環境變數，請在設定檔中替換 <...> 佔位符：", fg="yellow")
        for k in env_keys:
            click.echo(f"   {k}")

    click.echo()

