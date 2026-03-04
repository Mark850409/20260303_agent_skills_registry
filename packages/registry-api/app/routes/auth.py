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
    if not auth_header:
        # print("DEBUG: Missing Authorization header")
        return None
    if not auth_header.startswith("Bearer "):
        # print(f"DEBUG: Invalid header format: {auth_header[:10]}...")
        return None
    
    # 相容性考量：使用切片而非 removeprefix
    raw_token = auth_header[7:].strip()
    token_hash = _hash_token(raw_token)
    user = User.query.filter_by(api_token_hash=token_hash).first()
    if not user:
        # print("DEBUG: No user found for token hash")
        pass
    return user


def require_permission(perm):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                # 這裡要確保 get_current_user 失敗時拋出正確錯誤
                abort(401, message="Authentication required")
            
            # Admin role bypasses all checks
            if user.role == "admin":
                return f(*args, **kwargs)
            
            # 獲取權限清單
            user_perms = user.permissions or []
            # 如果是維護者且沒設定權限，預設給予基本權限
            if not user_perms and user.role == "maintainer":
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
            is_admin = (username == "admin")
            user = User(
                username=username, 
                email=email,
                role="admin" if is_admin else "maintainer",
                permissions=["*:*"] if is_admin else ["skill:create", "skill:update"]
            )
            db.session.add(user)
        else:
            is_admin = (username == "admin")
            if is_admin:
                user.role = "admin"
                user.permissions = ["*:*"]
            elif not user.permissions and user.role != "admin":
                # 向下兼容：替尚未有權限的現有用戶補上發布權限
                user.role = "maintainer"
                user.permissions = ["skill:create", "skill:update"]

        # Generate opaque API token
        import os
        raw_token = secrets.token_urlsafe(32)
        
        # 優先使用環境變數中的 Token (開發模式：確保與 CLI .env 一致)
        if username == "admin":
            env_token = os.environ.get("AGENTSKILLS_TOKEN")
            if env_token:
                raw_token = env_token

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
