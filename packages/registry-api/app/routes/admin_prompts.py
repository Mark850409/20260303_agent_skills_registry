from flask import Blueprint, request, jsonify
from flask_smorest import Blueprint as SmorestBlueprint
from marshmallow import Schema, fields
from app import db
from app.models import PromptSetting

bp = SmorestBlueprint("admin_prompts", __name__, description="Admin Operations on Prompt Settings", url_prefix="/api/admin/prompt-settings")

class PromptSettingSchema(Schema):
    id = fields.Integer(dump_only=True)
    category = fields.String(required=True)
    name = fields.String(required=True)
    group_name = fields.String(missing=None)
    content = fields.String(missing=None)
    is_active = fields.Boolean(missing=True)
    order_index = fields.Integer(missing=0)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class PromptSettingUpdateSchema(Schema):
    category = fields.String(required=False)
    name = fields.String(required=False)
    group_name = fields.String(required=False, allow_none=True)
    content = fields.String(required=False, allow_none=True)
    is_active = fields.Boolean(required=False)
    order_index = fields.Integer(required=False)

@bp.route("", methods=["GET"])
@bp.response(200, PromptSettingSchema(many=True))
def list_settings():
    """List all prompt settings."""
    category = request.args.get("category")
    query = PromptSetting.query
    if category:
        query = query.filter_by(category=category)
    settings = query.order_by(PromptSetting.order_index, PromptSetting.id).all()
    return settings

@bp.route("", methods=["POST"])
@bp.arguments(PromptSettingSchema)
@bp.response(201, PromptSettingSchema)
def create_setting(kwargs):
    """Create a new prompt setting."""
    setting = PromptSetting(**kwargs)
    db.session.add(setting)
    db.session.commit()
    return setting

@bp.route("/<int:setting_id>", methods=["PUT"])
@bp.arguments(PromptSettingUpdateSchema)
@bp.response(200, PromptSettingSchema)
def update_setting(kwargs, setting_id):
    """Update a prompt setting."""
    setting = PromptSetting.query.get_or_404(setting_id)
    for key, value in kwargs.items():
        setattr(setting, key, value)
    db.session.commit()
    return setting

@bp.route("/<int:setting_id>", methods=["DELETE"])
@bp.response(204)
def delete_setting(setting_id):
    """Delete a prompt setting."""
    setting = PromptSetting.query.get_or_404(setting_id)
    db.session.delete(setting)
    db.session.commit()
    return ""

public_bp = Blueprint("public_prompts", __name__, url_prefix="/api/prompt-settings")

@public_bp.route("/public", methods=["GET"])
def get_public_settings():
    """Get active prompt settings grouped by category for the generator UI."""
    settings = PromptSetting.query.filter_by(is_active=True).order_by(PromptSetting.order_index, PromptSetting.id).all()
    
    result = {
        "scenarios": [],
        "formats": [],
        "tones": [],
        "constraints": [],
        "roleGroups": {}
    }
    
    for s in settings:
        if s.category == "scenario":
            result["scenarios"].append({"id": s.group_name or s.name, "name": s.name})
        elif s.category == "format":
            result["formats"].append(s.name)
        elif s.category == "tone":
            result["tones"].append(s.name)
        elif s.category == "constraint":
            result["constraints"].append(s.name)
        elif s.category == "role":
            group = s.group_name or "未分類"
            if group not in result["roleGroups"]:
                result["roleGroups"][group] = []
            result["roleGroups"][group].append(s.name)
            
    return jsonify(result)
