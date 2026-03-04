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
    {"id": "coding",       "label": "程式開發",     "icon": "💻"},
    {"id": "web",          "label": "Web / UI",    "icon": "🌐"},
    {"id": "data",         "label": "資料分析",     "icon": "📊"},
    {"id": "writing",      "label": "文案 / 文件",  "icon": "✍️"},
    {"id": "ai",           "label": "AI / Agent",  "icon": "🤖"},
    {"id": "design",       "label": "設計 / 創作",  "icon": "🎨"},
    {"id": "productivity", "label": "效率工具",     "icon": "⚡"},
    {"id": "devops",       "label": "DevOps",      "icon": "🛠️"},
]

CATEGORY_IDS = [c["id"] for c in CATEGORIES]


def auto_classify(skill: Skill) -> str | None:
    """以啟發式規則自動判斷技能分類，回傳 category id 或 None。"""
    text = " ".join([
        skill.name or "",
        skill.description or "",
        " ".join(skill.tags or [])
    ]).lower()

    rules = [
        ("devops",       r"devops|docker|deploy|kubernetes|k8s|cloud|infra|ci.cd|pipeline"),
        ("data",         r"data|analytics|excel|xlsx|csv|spreadsheet|chart|database|sql|etl|bi"),
        ("writing",      r"\bdoc\b|docs|documentation|writing|report|blog|markdown|pdf|word|docx|pptx|slide|coauthor|letter"),
        ("web",          r"web|html|css|frontend|browser|ui |ux |playwright|webapp|artifact|react|vue|tailwind"),
        ("design",       r"design|art\b|image|graphic|illustrat|generative|algorithmic|poster|brand|theme|visual|gif|p5\.js"),
        ("productivity", r"productivity|communic|slack|email|meeting|planning|internal.comm"),
        ("ai",           r"\bai\b|llm|rag|knowledge.base|mcp|agent.skill|retriev|embed|vector|prompt"),
        ("coding",       r"code|coding|program|test|debug|refactor|review|\bgit\b|javascript|python|typescript|lint|build|script|macro|recorder|cli"),
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
        
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user


@admin_blp.route("/users/<int:user_id>")
class AdminUserDetail(MethodView):
    @admin_blp.arguments(UserUpdateSchema)
    @admin_blp.response(200, UserSchema)
    @require_permission("admin:access")
    def patch(self, data, user_id):
        """[管理員] 修改使用者資訊（用戶名、Email、角色、權限）"""
        user = User.query.get_or_404(user_id)
        
        # 防止用戶名衝突
        if "username" in data and data["username"] != user.username:
            if User.query.filter_by(username=data["username"]).first():
                abort(409, message="Username already exists")

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
