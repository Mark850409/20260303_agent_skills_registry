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
        "formatGroups": {},
        "toneGroups": {},
        "constraintGroups": {},
        "roleGroups": {}
    }
    
    for s in settings:
        group = s.group_name or "通用" # fallback group
        
        if s.category == "scenario":
            # Pass group_name along with the scenario so the frontend knows how to filter others
            result["scenarios"].append({"id": s.name, "name": s.name, "group": group})
        elif s.category == "format":
            if group not in result["formatGroups"]:
                result["formatGroups"][group] = []
            result["formatGroups"][group].append(s.name)
        elif s.category == "tone":
            if group not in result["toneGroups"]:
                result["toneGroups"][group] = []
            result["toneGroups"][group].append(s.name)
        elif s.category == "constraint":
            if group not in result["constraintGroups"]:
                result["constraintGroups"][group] = []
            result["constraintGroups"][group].append(s.name)
        elif s.category == "role":
            if group not in result["roleGroups"]:
                result["roleGroups"][group] = []
            result["roleGroups"][group].append(s.name)
            
    return jsonify(result)
