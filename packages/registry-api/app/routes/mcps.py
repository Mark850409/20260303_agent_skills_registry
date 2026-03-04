"""MCP Server Registry 公開路由。"""
import json
from flask import Response, stream_with_context, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
import httpx
from sqlalchemy import func, or_

from app import db
from app.models import MCPServer
from app.schemas import (
    MCPSchema, MCPQuerySchema, MCPListResponseSchema,
    MCPPublishSchema, MCPUpdateSchema,
)
from app.routes.auth import require_permission, get_current_user
from app.mcp_helper import introspect_mcp_tools, run_introspection_task

mcps_blp = Blueprint("mcps", __name__, url_prefix="/api/mcps", description="MCP Server Registry")


@mcps_blp.route("")
class MCPList(MethodView):

    @mcps_blp.arguments(MCPQuerySchema, location="query")
    @mcps_blp.response(200, MCPListResponseSchema)
    def get(self, args):
        """列出 MCP Servers（支援搜尋 / 分類 / transport 過濾）"""
        q        = args.get("q", "")
        category = args.get("category", "")
        tags_q   = args.get("tags", "")
        transport = args.get("transport", "")
        sort     = args.get("sort", "installs")
        page     = args.get("page", 1)
        per_page = args.get("per_page", 20)

        query = MCPServer.query

        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                MCPServer.name.ilike(like),
                MCPServer.display_name.ilike(like),
                MCPServer.description.ilike(like),
                MCPServer.author.ilike(like),
            ))
        if category:
            query = query.filter(MCPServer.category == category)
        if transport:
            query = query.filter(MCPServer.transport == transport)
        if tags_q:
            for tag in tags_q.split(","):
                tag = tag.strip()
                if tag:
                    query = query.filter(MCPServer.tags.contains([tag]))

        sort_map = {
            "installs":   MCPServer.installs.desc(),
            "created_at": MCPServer.created_at.desc(),
            "name":       MCPServer.name.asc(),
        }
        query = query.order_by(sort_map.get(sort, MCPServer.installs.desc()))

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "mcps":     paginated.items,
            "total":    paginated.total,
            "page":     paginated.page,
            "pages":    paginated.pages,
            "per_page": per_page,
        }

    @mcps_blp.arguments(MCPPublishSchema)
    @mcps_blp.response(201, MCPSchema)
    def post(self, data):
        """發布新的 MCP Server"""
        user = get_current_user()
        if not user:
            abort(401, message="Authentication required")
        if user.role != "admin" and "skill:create" not in (user.permissions or []):
            abort(403, message="Permission denied: skill:create")

        existing = MCPServer.query.filter_by(name=data["name"]).first()
        if existing:
            abort(409, message=f"MCP server '{data['name']}' already exists")

        local_configs = data.get("local_config", [])
        introspection_envs = {}
        
        # 提取 env_values 用於背景內省，但不存入資料庫以確保安全
        # 注意：這裡我們建立一個清洗過的 local_config 清單，稍後放回 data 中
        cleaned_configs = []
        for lc in local_configs:
            # 必須淺拷貝以免更動到原有的 data[] (雖然 data 之後沒用了但保險起見)
            lc_cleaned = lc.copy()
            if "env_values" in lc_cleaned:
                v = lc_cleaned.pop("env_values")
                if isinstance(v, dict):
                    introspection_envs.update(v)
            cleaned_configs.append(lc_cleaned)
        
        # 把清洗後的版本補回 data，稍後 server 模型初始化會用到
        data["local_config"] = cleaned_configs

        server = MCPServer(
            name          = data["name"],
            display_name  = data["display_name"],
            description   = data["description"],
            author        = data["author"],
            license       = data.get("license", "MIT"),
            repository    = data.get("repository"),
            endpoint_url  = data.get("endpoint_url"),
            transport     = data.get("transport", "sse"),
            category      = data.get("category"),
            tags          = data.get("tags", []),
            tools         = data.get("tools", []),
            local_config  = cleaned_configs,
            latest_version = data.get("latest_version", "1.0.0"),
            owner_id      = user.id,
        )
        db.session.add(server)
        db.session.commit() # 先存檔，拿到 ID
        
        # ── 背景自動偵測工具 (Introspection) ──
        if not server.tools:
            # 使用背景執行緒避免 API 阻塞，並傳入驗證用的環境變數
            run_introspection_task(server.id, env_values=introspection_envs)

        return server


@mcps_blp.route("/<string:name>")
class MCPDetail(MethodView):

    @mcps_blp.response(200, MCPSchema)
    def get(self, name):
        """取得 MCP Server 詳情"""
        server = MCPServer.query.filter_by(name=name).first_or_404()
        return server

    @mcps_blp.arguments(MCPUpdateSchema)
    @mcps_blp.response(200, MCPSchema)
    @require_permission("skill:update")
    def patch(self, data, name):
        """更新 MCP Server 資訊"""
        user = get_current_user()
        server = MCPServer.query.filter_by(name=name).first_or_404()
        
        # 權限檢查：只有管理員或擁有者可以修改
        if user.role != "admin" and server.owner_id != user.id:
            abort(403, message="You do not own this MCP server")

        for field in ("display_name", "description", "author", "license",
                      "repository", "endpoint_url", "transport", "category",
                      "tags", "tools", "local_config"):
            if field in data and data[field] is not None:
                setattr(server, field, data[field])

        # ── 背景重新偵測工具 (如果相關欄位變動且未提供 tools) ──
        tools_relevant_changed = any(k in data for k in ("transport", "endpoint_url", "local_config"))
        if tools_relevant_changed and "tools" not in data:
            run_introspection_task(server.id)

        db.session.commit()
        return server

    @mcps_blp.response(204)
    def delete(self, name):
        """刪除 MCP Server（管理員）"""
        user = get_current_user()
        if not user:
            abort(401, message="Authentication required")
        if user.role != "admin":
            abort(403, message="Admin only")
        server = MCPServer.query.filter_by(name=name).first_or_404()
        db.session.delete(server)
        db.session.commit()


@mcps_blp.route("/<string:name>/connect")
class MCPConnect(MethodView):

    def get(self, name):
        """取得 MCP Server 連線資訊（SSE URL + 本地啟動指令 + Claude config）"""
        server = MCPServer.query.filter_by(name=name).first_or_404()

        # 計算 SSE 代理 URL（優先用 AGENTSKILLS_REGISTRY 環境變數）
        import os as _os
        from flask import request as req
        registry_base = _os.environ.get("AGENTSKILLS_REGISTRY", "").rstrip("/")
        if not registry_base:
            registry_base = req.host_url.rstrip("/")
        sse_proxy_url = f"{registry_base}/api/mcps/{name}/sse"

        # 組合各種本地啟動的 Claude Desktop config
        claude_configs = {}

        # Remote / SSE
        if server.endpoint_url or server.transport == "sse":
            claude_configs["remote"] = {
                "url": server.endpoint_url or sse_proxy_url,
            }

        # 依 local_config 清單建立 claude config
        for lc in (server.local_config or []):
            t = lc.get("type", "")
            cmd = lc.get("command", "")
            pkg = lc.get("package", "")
            img = lc.get("image", "")
            env_keys = lc.get("env", [])

            if t == "node" and pkg:
                claude_configs["node"] = {
                    "command": "npx",
                    "args": ["-y", pkg],
                    "env": {k: f"<your-{k.lower()}>" for k in env_keys},
                }
            elif t == "python" and pkg:
                claude_configs["python"] = {
                    "command": "python",
                    "args": ["-m", pkg.replace("-", "_").replace("/", ".")],
                    "env": {k: f"<your-{k.lower()}>" for k in env_keys},
                }
            elif t == "docker" and img:
                claude_configs["docker"] = {
                    "command": "docker",
                    "args": ["run", "-i", "--rm",
                             *[item for k in env_keys for item in ["-e", f"{k}=<your-{k.lower()}>"]],
                             img],
                }

        # 安裝次數 +1
        server.installs = (server.installs or 0) + 1
        db.session.commit()

        return {
            "name":           server.name,
            "display_name":   server.display_name,
            "endpoint_url":   server.endpoint_url,
            "sse_proxy_url":  sse_proxy_url,
            "transport":      server.transport,
            "local_config":   server.local_config or [],
            "claude_configs": claude_configs,
        }


@mcps_blp.route("/<string:name>/sse")
class MCPSSEProxy(MethodView):

    def get(self, name):
        """SSE 代理端點：若 server 有 endpoint_url，則 proxy；否則回傳心跳流"""
        server = MCPServer.query.filter_by(name=name).first_or_404()

        if server.endpoint_url:
            # Proxy 到真實 MCP SSE endpoint
            target = server.endpoint_url.rstrip("/") + "/sse" \
                if not server.endpoint_url.endswith("/sse") else server.endpoint_url

            def _proxy():
                with httpx.stream("GET", target, timeout=None,
                                  headers={"Accept": "text/event-stream"}) as resp:
                    for chunk in resp.iter_text():
                        yield chunk

            return Response(
                stream_with_context(_proxy()),
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )
        else:
            # 回傳簡單心跳流（測試用）
            def _heartbeat():
                import time
                yield f"data: {{\"type\":\"ready\",\"server\":\"{name}\"}}\n\n"
                while True:
                    yield f"data: {{\"type\":\"ping\"}}\n\n"
                    time.sleep(15)

            return Response(
                stream_with_context(_heartbeat()),
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )


@mcps_blp.route("/<string:name>/messages")
class MCPMessages(MethodView):

    def post(self, name):
        """轉發 JSON-RPC message 到真實 MCP Server"""
        server = MCPServer.query.filter_by(name=name).first_or_404()
        if not server.endpoint_url:
            abort(400, message="This MCP server does not have a remote endpoint")

        payload = request.get_json(force=True)
        target = server.endpoint_url.rstrip("/") + "/messages"
        try:
            resp = httpx.post(target, json=payload, timeout=30)
            return Response(resp.content, status=resp.status_code,
                            content_type=resp.headers.get("content-type", "application/json"))
        except httpx.RequestError as e:
            abort(502, message=f"Failed to reach MCP server: {e}")


@mcps_blp.route("/tags")
class MCPTags(MethodView):

    def get(self):
        """取得 MCP 熱門標籤"""
        servers = MCPServer.query.all()
        counts = {}
        for s in servers:
            for t in (s.tags or []):
                counts[t] = counts.get(t, 0) + 1
        sorted_tags = sorted(counts.items(), key=lambda x: -x[1])
        return [{"tag": t, "count": c} for t, c in sorted_tags[:50]]


@mcps_blp.route("/stats")
class MCPStats(MethodView):

    def get(self):
        """全站 MCP 統計"""
        total = MCPServer.query.count()
        total_installs = db.session.query(func.sum(MCPServer.installs)).scalar() or 0
        return {"total_mcps": total, "total_installs": total_installs}


@mcps_blp.route("/categories")
class MCPCategories(MethodView):

    def get(self):
        """回傳 MCP 預設分類清單"""
        return [
            {"id": "web_search",    "icon": "🔍", "label": "Web Search"},
            {"id": "browser",       "icon": "🌐", "label": "Browser Automation"},
            {"id": "data",          "icon": "📊", "label": "Data & Analytics"},
            {"id": "coding",        "icon": "💻", "label": "Coding & Dev Tools"},
            {"id": "productivity",  "icon": "⚡", "label": "Productivity"},
            {"id": "ai",            "icon": "🤖", "label": "AI & Agents"},
            {"id": "database",      "icon": "🗄️", "label": "Database"},
            {"id": "communication", "icon": "💬", "label": "Communication"},
            {"id": "cloud",         "icon": "☁️", "label": "Cloud & DevOps"},
            {"id": "other",         "icon": "🧩", "label": "Other"},
        ]
