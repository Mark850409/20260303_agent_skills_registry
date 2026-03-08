from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from app import db
from app.models import Skill, User
from app.routes.auth import require_permission
from app.schemas import (
    SkillSchema, 
    SkillQuerySchema, 
    SkillListResponseSchema, 
    SkillUpdateSchema,
    UserSchema,
    UserUpdateSchema,
    UserQuerySchema,
    UserListResponseSchema,
    UserCreateSchema
)

admin_blp = Blueprint("admin", __name__, url_prefix="/api/admin", description="Administration operations")


# ── 預設分類定義 ────────────────────────────────────────────────────
CATEGORIES = [
    {"id": "coding",        "label": "程式開發",     "icon": "💻"},
    {"id": "web",           "label": "Web 瀏覽",    "icon": "🌐"},
    {"id": "search",        "label": "網路搜尋",     "icon": "🔍"},
    {"id": "data",          "label": "資料分析",     "icon": "📊"},
    {"id": "database",      "label": "資料庫",      "icon": "🗄️"},
    {"id": "ai",            "label": "AI 智能",      "icon": "🤖"},
    {"id": "productivity",  "label": "效率工具",     "icon": "⚡"},
    {"id": "writing",       "label": "文案文件",     "icon": "✍️"},
    {"id": "design",        "label": "設計創作",     "icon": "🎨"},
    {"id": "devops",        "label": "運維部署",     "icon": "🛠️"},
    {"id": "communication", "label": "通訊聯絡",     "icon": "💬"},
    {"id": "maps",          "label": "地圖數據",     "icon": "📍"},
    {"id": "finance",       "label": "金融科技",     "icon": "💰"},
    {"id": "science",       "label": "科學計算",     "icon": "🧪"},
    {"id": "travel",        "label": "旅遊生活",     "icon": "✈️"},
    {"id": "health",        "label": "健康醫療",     "icon": "🏥"},
    {"id": "other",         "label": "其他",        "icon": "📦"},
]

CATEGORY_IDS = [c["id"] for c in CATEGORIES]


def auto_classify(target) -> str | None:
    """以啟發式規則自動判斷分類，回傳 category id 或 None。支援 Skill 或 MCPServer 物件。"""
    name = getattr(target, "name", "")
    description = getattr(target, "description", "")
    display_name = getattr(target, "display_name", "")
    tags = getattr(target, "tags", [])
    
    text = " ".join([
        name or "",
        display_name or "",
        description or "",
        " ".join(tags or [])
    ]).lower()

    rules = [
        ("devops",       r"devops|docker|deploy|kubernetes|k8s|cloud|infra|ci.cd|pipeline"),
        ("data",         r"data|analytics|excel|xlsx|csv|spreadsheet|chart|etl|bi"),
        ("database",     r"database|sql|mysql|postgres|sqlite|query|storage|mongodb|redis|prisma"),
        ("maps",         r"map|geo|location|address|gps|place|route|navigation|earth"),
        ("finance",      r"finance|crypto|stock|trading|wallet|payment|billing|stripe|bank|tax"),
        ("communication",r"slack|email|mail|discord|telegram|message|notification|chat|twilio"),
        ("science",      r"science|math|calculation|physics|chem|biology|research|statist"),
        ("travel",       r"travel|flight|hotel|booking|restaurant|food|weather|lifestyle"),
        ("health",       r"health|fitness|medical|doctor|hospital|workout|nutrition"),
        ("writing",      r"\bdoc\b|docs|documentation|writing|report|blog|markdown|pdf|word|docx|pptx|slide|coauthor|letter"),
        ("search",       r"search|exa\b|google|bing|tavily|duckduckgo|web.search"),
        ("web",          r"web|html|css|frontend|browser\b|ui |ux |playwright|webapp|artifact|react|vue|tailwind"),
        ("design",       r"design|art\b|image|graphic|illustrat|generative|algorithmic|poster|brand|theme|visual|gif|p5\.js"),
        ("productivity", r"productivity|planning|task|calendar|workflow|project|todo|notion"),
        ("ai",           r"\bai\b|llm|rag|knowledge.base|mcp|agent.skill|retriev|embed|vector|prompt|openai|anthropic|gemini"),
        ("coding",       r"code|coding|program|test|debug|refactor|review|\bgit\b|javascript|python|typescript|lint|build|script|macro|recorder|cli|terminal|shell|npx|pip"),
    ]
    import re
    for cat_id, pattern in rules:
        if re.search(pattern, text):
            return cat_id
    return None


# ── 分類清單端點 ────────────────────────────────────────────────────
class CategoryListSchema(Schema):
    id = fields.String()
    label = fields.String()
    icon = fields.String()


@admin_blp.route("/categories")
class AdminCategories(MethodView):
    @admin_blp.response(200, CategoryListSchema(many=True))
    def get(self):
        """取得預設分類清單"""
        return CATEGORIES


# ── 技能管理端點 ────────────────────────────────────────────────────
@admin_blp.route("/skills")
class AdminSkills(MethodView):
    @admin_blp.arguments(SkillQuerySchema, location="query")
    @admin_blp.response(200, SkillListResponseSchema)
    @require_permission("admin:access")
    def get(self, args):
        """[管理員] 列出所有技能"""
        q = args.get("q", "").strip()
        sort = args.get("sort", "created_at")
        page = args.get("page", 1)
        per_page = args.get("per_page", 50)

        query = Skill.query

        if q:
            query = query.filter(
                db.or_(
                    Skill.name.ilike(f"%{q}%"),
                    Skill.description.ilike(f"%{q}%")
                )
            )

        # Default admin sort: newest first
        query = query.order_by(Skill.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "skills": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }


# ── 批次 AI 自動分類 ────────────────────────────────────────────────
class ClassifyAllResponseSchema(Schema):
    classified = fields.Integer()
    skipped = fields.Integer()
    details = fields.List(fields.Dict())


@admin_blp.route("/skills/classify-all")
class AdminSkillsClassifyAll(MethodView):
    @admin_blp.response(200, ClassifyAllResponseSchema)
    @require_permission("admin:access")
    def post(self):
        """[管理員] AI 批次自動分類所有技能（強制覆蓋現有分類）"""
        skills = Skill.query.all()
        classified = 0
        skipped = 0
        details = []

        for skill in skills:
            cat = auto_classify(skill)
            if cat:
                skill.category = cat
                classified += 1
                details.append({"name": skill.name, "category": cat})
            else:
                skipped += 1

        db.session.commit()
        return {"classified": classified, "skipped": skipped, "details": details}


# ── 單筆技能管理 ────────────────────────────────────────────────────
@admin_blp.route("/skills/<string:name>")
class AdminSkillDetail(MethodView):
    @admin_blp.response(200, SkillSchema)
    @require_permission("admin:access")
    def get(self, name):
        """[管理員] 取得技能詳情"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        return skill

    @admin_blp.arguments(SkillUpdateSchema)
    @admin_blp.response(200, SkillSchema)
    @require_permission("admin:access")
    def patch(self, data, name):
        """[管理員] 修改技能元數據（含 category）"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        
        for key, value in data.items():
            setattr(skill, key, value)
            
        db.session.commit()
        return skill

    @admin_blp.response(204)
    @require_permission("admin:access")
    def delete(self, name):
        """[管理員] 永久刪除技能及其所有版本"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        db.session.delete(skill)
        db.session.commit()
        return ""


# ── 單筆 AI 自動分類 ────────────────────────────────────────────────
class ClassifyOneResponseSchema(Schema):
    name = fields.String()
    category = fields.String(allow_none=True)
    changed = fields.Boolean()


@admin_blp.route("/skills/<string:name>/classify")
class AdminSkillClassify(MethodView):
    @admin_blp.response(200, ClassifyOneResponseSchema)
    @require_permission("admin:access")
    def post(self, name):
        """[管理員] AI 自動分類單一技能"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        old_cat = skill.category
        cat = auto_classify(skill)
        skill.category = cat
        db.session.commit()
        return {"name": skill.name, "category": cat, "changed": old_cat != cat}


# ── 使用者管理 ───────────────────────────────────────────────────────
@admin_blp.route("/users")
class AdminUsers(MethodView):
    @admin_blp.arguments(UserQuerySchema, location="query")
    @admin_blp.response(200, UserListResponseSchema)
    @require_permission("admin:access")
    def get(self, args):
        """[管理員] 列出所有使用者（支援分頁與搜尋）"""
        q = args.get("q", "").strip()
        page = args.get("page", 1)
        per_page = args.get("per_page", 20)

        query = User.query

        if q:
            query = query.filter(
                db.or_(
                    User.username.ilike(f"%{q}%"),
                    User.email.ilike(f"%{q}%")
                )
            )

        query = query.order_by(User.id.asc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "users": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }

    @admin_blp.arguments(UserCreateSchema)
    @admin_blp.response(201, UserSchema)
    @require_permission("admin:access")
    def post(self, data):
        """[管理員] 手動新增使用者"""
        if User.query.filter_by(username=data["username"]).first():
            abort(409, message="Username already exists")
        
        from werkzeug.security import generate_password_hash
        password = data.pop("password")
        
        user = User(**data)
        user.password_hash = generate_password_hash(password)
        
        db.session.add(user)
        db.session.commit()
        return user


@admin_blp.route("/users/<int:user_id>")
class AdminUserDetail(MethodView):
    @admin_blp.arguments(UserUpdateSchema)
    @admin_blp.response(200, UserSchema)
    @require_permission("admin:access")
    def patch(self, data, user_id):
        """[管理員] 修改使用者資訊（用戶名、Email、角色、權限、密碼）"""
        user = User.query.get_or_404(user_id)
        
        # 防止用戶名衝突
        if "username" in data and data["username"] != user.username:
            if User.query.filter_by(username=data["username"]).first():
                abort(409, message="Username already exists")

        # 處理密碼變更
        if "password" in data:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(data.pop("password"))

        for key, value in data.items():
            setattr(user, key, value)
            
        db.session.commit()
        return user

    @admin_blp.response(204)
    @require_permission("admin:access")
    def delete(self, user_id):
        """[管理員] 刪除使用者"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return ""
# ── MCP 管理端點 ───────────────────────────────────────────────────
from app.models import MCPServer
from app.schemas import (
    MCPSchema, MCPQuerySchema, MCPListResponseSchema, MCPUpdateSchema
)

@admin_blp.route("/mcps")
class AdminMCPs(MethodView):
    @admin_blp.arguments(MCPQuerySchema, location="query")
    @admin_blp.response(200, MCPListResponseSchema)
    @require_permission("admin:access")
    def get(self, args):
        """[管理員] 列出所有 MCP Servers"""
        q = args.get("q", "").strip()
        sort = args.get("sort", "created_at")
        page = args.get("page", 1)
        per_page = args.get("per_page", 50)

        query = MCPServer.query

        if q:
            query = query.filter(
                db.or_(
                    MCPServer.name.ilike(f"%{q}%"),
                    MCPServer.display_name.ilike(f"%{q}%"),
                    MCPServer.description.ilike(f"%{q}%")
                )
            )

        query = query.order_by(MCPServer.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "mcps": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }

@admin_blp.route("/mcps/<string:name>")
class AdminMCPDetail(MethodView):
    @admin_blp.response(200, MCPSchema)
    @require_permission("admin:access")
    def get(self, name):
        """[管理員] 取得 MCP 詳情"""
        server = MCPServer.query.filter_by(name=name).first_or_404()
        return server

    @admin_blp.arguments(MCPUpdateSchema)
    @admin_blp.response(200, MCPSchema)
    @require_permission("admin:access")
    def patch(self, data, name):
        """[管理員] 修改 MCP 控制元數據"""
        server = MCPServer.query.filter_by(name=name).first_or_404()
        for key, value in data.items():
            if value is not None:
                setattr(server, key, value)
        db.session.commit()
        return server

    @admin_blp.response(204)
    @require_permission("admin:access")
    def delete(self, name):
        """[管理員] 永久刪除 MCP Server"""
        server = MCPServer.query.filter_by(name=name).first_or_404()
        db.session.delete(server)
        db.session.commit()
        return ""

@admin_blp.route("/mcps/classify-all")
class AdminMCPsClassifyAll(MethodView):
    @admin_blp.response(200, ClassifyAllResponseSchema)
    @require_permission("admin:access")
    def post(self):
        """[管理員] AI 批次自動分類所有 MCP Servers"""
        servers = MCPServer.query.all()
        classified = 0
        skipped = 0
        details = []

        for s in servers:
            cat = auto_classify(s)
            if cat:
                s.category = cat
                classified += 1
                details.append({"name": s.name, "category": cat})
            else:
                skipped += 1

        db.session.commit()
        return {"classified": classified, "skipped": skipped, "details": details}

# ── Docker Repository 管理端點 ────────────────────────────────────
from app.models import DockerRepository
from app.schemas import (
    DockerRepositorySchema, DockerRepositoryQuerySchema, 
    DockerRepositoryListResponseSchema, DockerRepositoryCreateSchema,
    DockerRepositoryUpdateSchema
)

@admin_blp.route("/docker-repos")
class AdminDockerRepos(MethodView):
    @admin_blp.arguments(DockerRepositoryQuerySchema, location="query")
    @admin_blp.response(200, DockerRepositoryListResponseSchema)
    @require_permission("admin:access")
    def get(self, args):
        """[管理員] 列出所有 Docker 倉庫"""
        q = args.get("q", "").strip()
        page = args.get("page", 1)
        per_page = args.get("per_page", 10)

        query = DockerRepository.query

        if q:
            query = query.filter(
                db.or_(
                    DockerRepository.name.ilike(f"%{q}%"),
                    DockerRepository.description.ilike(f"%{q}%")
                )
            )

        query = query.order_by(DockerRepository.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "repositories": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }

    @admin_blp.arguments(DockerRepositoryCreateSchema)
    @admin_blp.response(201, DockerRepositorySchema)
    @require_permission("admin:access")
    def post(self, data):
        """[管理員] 新增 Docker 倉庫"""
        if DockerRepository.query.filter_by(name=data["name"]).first():
            abort(409, message="Docker repository name already exists")
        
        repo = DockerRepository(**data)
        from flask import g
        if hasattr(g, 'user') and g.user:
            repo.owner_id = g.user.id

        db.session.add(repo)
        db.session.commit()
        return repo

@admin_blp.route("/docker-repos/<int:repo_id>")
class AdminDockerRepoDetail(MethodView):
    @admin_blp.arguments(DockerRepositoryUpdateSchema)
    @admin_blp.response(200, DockerRepositorySchema)
    @require_permission("admin:access")
    def patch(self, data, repo_id):
        """[管理員] 修改 Docker 倉庫描述"""
        repo = DockerRepository.query.get_or_404(repo_id)
        for key, value in data.items():
            if value is not None:
                setattr(repo, key, value)
        db.session.commit()
        return repo

    @admin_blp.response(204)
    @require_permission("admin:access")
    def delete(self, repo_id):
        """[管理員] 刪除 Docker 倉庫"""
        repo = DockerRepository.query.get_or_404(repo_id)
        repo_name = repo.name
        db.session.delete(repo)
        db.session.commit()
        
        # physically delete the repository from the mounted registry volume
        import os
        import shutil
        repo_path = f"/var/lib/registry/docker/registry/v2/repositories/{repo_name}"
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
        except Exception as e:
            print(f"Failed to delete physical repository directory {repo_path}: {e}")
            
        return ""

# ── Npm Package 管理端點 ───────────────────────────────────────────
from app.models import NpmPackage
from app.schemas import (
    NpmPackageSchema, NpmPackageQuerySchema, 
    NpmPackageListResponseSchema, NpmPackageCreateSchema,
    NpmPackageUpdateSchema
)

@admin_blp.route("/npm-packages")
class AdminNpmPackages(MethodView):
    @admin_blp.arguments(NpmPackageQuerySchema, location="query")
    @admin_blp.response(200, NpmPackageListResponseSchema)
    @require_permission("admin:access")
    def get(self, args):
        """[管理員] 列出所有 Npm 套件"""
        q = args.get("q", "").strip()
        page = args.get("page", 1)
        per_page = args.get("per_page", 10)

        query = NpmPackage.query

        if q:
            query = query.filter(
                db.or_(
                    NpmPackage.name.ilike(f"%{q}%"),
                    NpmPackage.description.ilike(f"%{q}%")
                )
            )

        query = query.order_by(NpmPackage.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "packages": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }

    @admin_blp.arguments(NpmPackageCreateSchema)
    @admin_blp.response(201, NpmPackageSchema)
    @require_permission("admin:access")
    def post(self, data):
        """[管理員] 新增 NPM 套件"""
        if NpmPackage.query.filter_by(name=data["name"]).first():
            abort(409, message="NPM package name already exists")
        
        pkg = NpmPackage(**data)
        from flask import g
        if hasattr(g, 'user') and g.user:
            pkg.owner_id = g.user.id

        db.session.add(pkg)
        db.session.commit()
        return pkg

@admin_blp.route("/npm-packages/<int:pkg_id>")
class AdminNpmPackageDetail(MethodView):
    @admin_blp.arguments(NpmPackageUpdateSchema)
    @admin_blp.response(200, NpmPackageSchema)
    @require_permission("admin:access")
    def patch(self, data, pkg_id):
        """[管理員] 修改 NPM 套件描述"""
        pkg = NpmPackage.query.get_or_404(pkg_id)
        for key, value in data.items():
            if value is not None:
                setattr(pkg, key, value)
        db.session.commit()
        return pkg

    @admin_blp.response(204)
    @require_permission("admin:access")
    def delete(self, pkg_id):
        """[管理員] 刪除 NPM 套件"""
        pkg = NpmPackage.query.get_or_404(pkg_id)
        db.session.delete(pkg)
        db.session.commit()
        return ""
