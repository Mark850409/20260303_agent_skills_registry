import os
import hashlib
import secrets
from flask import Blueprint, request, jsonify
from app import db
from app.models import User
import jwt
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint("auth", __name__)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@auth_bp.route("/login", methods=["POST"])
def login():
    """取得 API Token（開發模式：簡單用 username 建立 token）。"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()

    if not username or not email:
        return jsonify({"error": "username and email required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, email=email)
        db.session.add(user)

    # Generate opaque API token
    raw_token = secrets.token_urlsafe(32)
    user.api_token_hash = _hash_token(raw_token)
    db.session.commit()

    return jsonify({"api_token": raw_token, "username": username})


@auth_bp.route("/me", methods=["GET"])
def me():
    """驗證 API Token，回傳目前使用者資訊。"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    raw_token = auth_header.removeprefix("Bearer ").strip()
    token_hash = _hash_token(raw_token)
    user = User.query.filter_by(api_token_hash=token_hash).first()
    if not user:
        return jsonify({"error": "Invalid token"}), 401

    return jsonify({"username": user.username, "email": user.email})
