from flask import Blueprint, request, jsonify
from flask_smorest import Blueprint as SmorestBlueprint
from marshmallow import Schema, fields
from app import db
from app.models import PromptKnowledge

# Admin Blueprint for managing Prompt Knowledge Base
admin_knowledge_bp = SmorestBlueprint("admin_prompt_knowledge", __name__, description="Admin Operations on Prompt Knowledge Base", url_prefix="/api/admin/prompt-knowledge")

class PromptKnowledgeSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(missing=None)
    prompt_content = fields.String(required=True)
    tags = fields.List(fields.String(), missing=[])
    author_id = fields.Integer(dump_only=True)
    is_public = fields.Boolean(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class PromptKnowledgeUpdateSchema(Schema):
    title = fields.String(required=False)
    description = fields.String(required=False, allow_none=True)
    prompt_content = fields.String(required=False)
    tags = fields.List(fields.String(), required=False)
    is_public = fields.Boolean(required=False)

@admin_knowledge_bp.route("", methods=["GET"])
@admin_knowledge_bp.response(200, PromptKnowledgeSchema(many=True))
def list_admin_knowledge():
    """List all prompt knowledge entries for admin."""
    # TODO: Add pagination later if needed
    entries = PromptKnowledge.query.order_by(PromptKnowledge.id.desc()).all()
    result = []
    for e in entries:
        result.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "prompt_content": e.prompt_content,
            "tags": e.tags.split(",") if e.tags else [],
            "author_id": e.author_id,
            "is_public": e.is_public,
            "created_at": e.created_at,
            "updated_at": e.updated_at
        })
    return result

@admin_knowledge_bp.route("/<int:entry_id>", methods=["PUT"])
@admin_knowledge_bp.arguments(PromptKnowledgeUpdateSchema)
@admin_knowledge_bp.response(200, PromptKnowledgeSchema)
def update_admin_knowledge(kwargs, entry_id):
    """Update a prompt knowledge entry."""
    entry = PromptKnowledge.query.get_or_404(entry_id)
    for key, value in kwargs.items():
        if key == 'tags':
            value = ",".join(value) if value else ""
        setattr(entry, key, value)
    db.session.commit()
    # return a dict formatted for marshmallow to serialize
    return {
        "id": entry.id,
        "title": entry.title,
        "description": entry.description,
        "prompt_content": entry.prompt_content,
        "tags": entry.tags.split(",") if entry.tags else [],
        "author_id": entry.author_id,
        "is_public": entry.is_public,
        "created_at": entry.created_at,
        "updated_at": entry.updated_at
    }

@admin_knowledge_bp.route("/<int:entry_id>", methods=["DELETE"])
@admin_knowledge_bp.response(204)
def delete_admin_knowledge(entry_id):
    """Delete a prompt knowledge entry."""
    entry = PromptKnowledge.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return ""


# ── AI Auto-Tagging logic ───────────────────────────────────────────
def auto_tag(target: PromptKnowledge) -> list[str]:
    """啟發式規則自動產生標籤，回傳多個符合標籤的列表。"""
    title = getattr(target, "title", "") or ""
    desc = getattr(target, "description", "") or ""
    content = getattr(target, "prompt_content", "") or ""
    
    text = f"{title} {desc} {content}".lower()

    rules = [
        ("程式設計",       r"code|coding|program|test|debug|refactor|review|\bgit\b|javascript|python|typescript|lint|build|script|macro|sql|database|db\b|react|vue|html|css|frontend|backend"),
        ("文章寫作",       r"寫作|文章|部落格|blog|write|writing|doc\b|docs|documentation|report|email|letter|copywriting|seo|翻譯|translate"),
        ("角色扮演",       r"扮演|專家|顧問|role|expert|consultant|act as|persona\b|性格|character"),
        ("商業行銷",       r"行銷|商業|社群|marketing|business|social media|twitter|facebook|instagram|linkedin|廣告|ads|sales|銷售"),
        ("學習教育",       r"學習|教學|解釋|learn|teach|explain|tutor|course|課程|student|teacher|education"),
        ("資料分析",       r"分析|資料|數據|analyze|analytics|data\b|excel|csv|chart|圖表|統計|statistics|summarize|總結|摘要"),
        ("創意企劃",       r"創意|腦力激盪|企劃|idea|brainstorm|creative|plan\b|策劃|活動|event"),
        ("生活實用",       r"旅行|行程|食譜|travel|recipe|food|health|健康|fitness|workout|運動|規劃|planning|organize"),
    ]
    
    import re
    tags = []
    for tag_name, pattern in rules:
        if re.search(pattern, text):
            tags.append(tag_name)
            
    return tags

class ClassifyAllResponseSchema(Schema):
    classified = fields.Integer()
    skipped = fields.Integer()
    details = fields.List(fields.Dict())

@admin_knowledge_bp.route("/classify-all", methods=["POST"])
@admin_knowledge_bp.response(200, ClassifyAllResponseSchema)
def classify_all_prompt_knowledge():
    """AI 批次自動為未標籤或既有的提示詞加上標籤 (強制合併)"""
    entries = PromptKnowledge.query.all()
    classified = 0
    skipped = 0
    details = []

    for entry in entries:
        existing_tags = set(entry.tags.split(",")) if entry.tags else set()
        new_tags = set(auto_tag(entry))
        
        # 合併現有標籤與新產生的標籤
        merged_tags = existing_tags.union(new_tags)
        
        # 去除空字串
        merged_tags = {t.strip() for t in merged_tags if t.strip()}
        
        if merged_tags != existing_tags:
            entry.tags = ",".join(sorted(list(merged_tags)))
            classified += 1
            details.append({"title": entry.title, "tags": list(merged_tags)})
        else:
            skipped += 1

    db.session.commit()
    return {"classified": classified, "skipped": skipped, "details": details}


# Public Blueprint for Prompt Knowledge Base
public_knowledge_bp = Blueprint("public_prompt_knowledge", __name__, url_prefix="/api/prompts/knowledge")

@public_knowledge_bp.route("/public", methods=["GET"])
def list_public_knowledge():
    """List all active/public prompt knowledge entries for users."""
    search = request.args.get("search", "")
    tag = request.args.get("tag", "")
    
    query = PromptKnowledge.query.filter_by(is_active=True) if hasattr(PromptKnowledge, 'is_active') else PromptKnowledge.query.filter_by(is_public=True)
    
    if search:
        query = query.filter((PromptKnowledge.title.ilike(f"%{search}%")) | (PromptKnowledge.description.ilike(f"%{search}%")) | (PromptKnowledge.prompt_content.ilike(f"%{search}%")))
    
    if tag:
        query = query.filter(PromptKnowledge.tags.ilike(f"%{tag}%"))
    
    entries = query.order_by(PromptKnowledge.id.desc()).all()
    
    return jsonify([entry.to_dict() for entry in entries])

@public_knowledge_bp.route("", methods=["POST"])
def create_public_knowledge():
    """Save a generated prompt to the knowledge base."""
    data = request.json
    
    if not data or not data.get("title") or not data.get("prompt_content"):
        return jsonify({"message": "Missing required fields (title, prompt_content)"}), 400
        
    tags_str = ""
    if "tags" in data and isinstance(data["tags"], list):
        tags_str = ",".join(data["tags"])
        
    entry = PromptKnowledge(
        title=data["title"],
        description=data.get("description", ""),
        prompt_content=data["prompt_content"],
        tags=tags_str,
        is_public=True
        # author_id could be set if user is logged in, leaving null for now for anonymous saving
    )
    db.session.add(entry)
    db.session.commit()
    
    return jsonify(entry.to_dict()), 201
