import hashlib
import secrets
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app import db
from app.models import User
from app.schemas import AuthLoginSchema, AuthTokenSchema, UserSchema

auth_blp = Blueprint("auth", __name__, url_prefix="/api/auth", description="Authentication operations")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    raw_token = auth_header.removeprefix("Bearer ").strip()
    token_hash = _hash_token(raw_token)
    return User.query.filter_by(api_token_hash=token_hash).first()


def require_permission(perm):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                abort(401, message="Authentication required")
            
            # Admin role bypasses all checks
            if user.role == "admin":
                return f(*args, **kwargs)
            
            # 為了向下相容：如果非 admin 用戶的權限欄位是空的，視為具有基本發布能力
            user_perms = user.permissions or []
            if not user_perms and user.role != "admin":
                user_perms = ["skill:create", "skill:update"]

            # Check for specific permission bit
            if perm in user_perms:
                return f(*args, **kwargs)
            
            abort(403, message=f"Permission denied: {perm}")
        return wrapper
    return decorator


@auth_blp.route("/login")
class AuthLogin(MethodView):
    @auth_blp.arguments(AuthLoginSchema)
    @auth_blp.response(200, AuthTokenSchema)
    def post(self, data):
        """取得 API Token（開發模式：簡單用 username 建立 token）"""
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username, 
                email=email,
                role="maintainer",
                permissions=["skill:create", "skill:update"]
            )
            db.session.add(user)
        else:
            # 向下兼容：替尚未有權限的現有用戶補上發布權限
            if not user.permissions and user.role != "admin":
                user.role = "maintainer"
                user.permissions = ["skill:create", "skill:update"]

        # Generate opaque API token
        raw_token = secrets.token_urlsafe(32)
        user.api_token_hash = _hash_token(raw_token)
        db.session.commit()

        return {"api_token": raw_token, "username": username}


@auth_blp.route("/me")
class AuthMe(MethodView):
    @auth_blp.response(200, UserSchema)
    def get(self):
        """驗證 API Token，回傳目前使用者資訊"""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")

        raw_token = auth_header.removeprefix("Bearer ").strip()
        token_hash = _hash_token(raw_token)
        user = User.query.filter_by(api_token_hash=token_hash).first()
        if not user:
            abort(401, message="Invalid token")

        return user
