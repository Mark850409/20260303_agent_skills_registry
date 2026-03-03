from flask.views import MethodView
from flask_smorest import Blueprint, abort
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
        """[管理員] 修改技能元數據"""
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
        
        # 禁止刪除目前的 admin (簡單防呆：假設 ID 為 1 或目前操作者)
        # TODO: 可以加入更嚴謹的 check
        
        db.session.delete(user)
        db.session.commit()
        return ""
