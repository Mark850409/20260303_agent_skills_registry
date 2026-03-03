import os
import io
import hashlib
import tarfile
from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models import Skill, SkillVersion

skills_bp = Blueprint("skills", __name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "data/bundles")


# ── GET /api/skills ───────────────────────────────────────────────────────────
@skills_bp.route("", methods=["GET"])
def list_skills():
    """搜尋 / 列出 Skills，支援 q, tags, sort, page 參數。"""
    q = request.args.get("q", "").strip()
    tags_param = request.args.get("tags", "")
    sort = request.args.get("sort", "downloads")  # downloads | name | created_at
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    query = Skill.query

    if q:
        query = query.filter(
            db.or_(
                Skill.name.ilike(f"%{q}%"),
                Skill.description.ilike(f"%{q}%"),
                Skill.author.ilike(f"%{q}%"),
            )
        )

    if tags_param:
        tags = [t.strip() for t in tags_param.split(",") if t.strip()]
        for tag in tags:
            # SQLite 兼容的 JSON 陣列成員查詢
            query = query.filter(Skill.tags.like(f'%"{tag}"%'))

    sort_map = {
        "downloads": Skill.downloads.desc(),
        "name": Skill.name.asc(),
        "created_at": Skill.created_at.desc(),
        "updated_at": Skill.updated_at.desc(),
    }
    query = query.order_by(sort_map.get(sort, Skill.downloads.desc()))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "skills": [s.to_dict() for s in paginated.items],
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }
    )


# ── GET /api/skills/tags ──────────────────────────────────────────────────────
@skills_bp.route("/tags", methods=["GET"])
def list_tags():
    """列出所有標籤及統計數量。"""
    skills = Skill.query.all()
    tag_counts = {}
    for skill in skills:
        for tag in (skill.tags or []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return jsonify([{"tag": t, "count": c} for t, c in sorted_tags])


# ── GET /api/skills/stats ─────────────────────────────────────────────────────
@skills_bp.route("/stats", methods=["GET"])
def stats():
    """全站統計。"""
    total_skills = Skill.query.count()
    total_downloads = db.session.query(db.func.sum(Skill.downloads)).scalar() or 0
    return jsonify({"total_skills": total_skills, "total_downloads": total_downloads})


# ── GET /api/skills/<name> ────────────────────────────────────────────────────
@skills_bp.route("/<name>", methods=["GET"])
def get_skill(name):
    """取得 Skill 詳情（含最新版 SKILL.md）。"""
    skill = Skill.query.filter_by(name=name).first_or_404()
    return jsonify(skill.to_dict(detail=True))


# ── GET /api/skills/<name>/<version> ─────────────────────────────────────────
@skills_bp.route("/<name>/<version>", methods=["GET"])
def get_skill_version(name, version):
    """取得特定版本詳情。"""
    skill = Skill.query.filter_by(name=name).first_or_404()
    sv = SkillVersion.query.filter_by(skill_id=skill.id, version=version).first_or_404()
    data = skill.to_dict()
    data["skill_md"] = sv.skill_md
    data["version"] = sv.version
    data["checksum"] = sv.checksum
    return jsonify(data)


# ── GET /api/skills/<name>/download (or /<version>) ──────────────────────────
@skills_bp.route("/<name>/download", methods=["GET"])
@skills_bp.route("/<name>/<version>/download", methods=["GET"])
def download_skill(name, version=None):
    """下載 Skill Bundle tar.gz。"""
    skill = Skill.query.filter_by(name=name).first_or_404()
    if version:
        sv = SkillVersion.query.filter_by(skill_id=skill.id, version=version).first_or_404()
    else:
        sv = (
            SkillVersion.query.filter_by(skill_id=skill.id)
            .order_by(SkillVersion.published_at.desc())
            .first_or_404()
        )

    # Increment downloads
    skill.downloads += 1
    db.session.commit()

    bundle_path = sv.bundle_path
    if bundle_path and os.path.exists(bundle_path):
        return send_file(
            bundle_path,
            mimetype="application/gzip",
            as_attachment=True,
            download_name=f"{name}-{sv.version}.tar.gz",
        )

    # Re-generate from skill_md if bundle file missing
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        md_bytes = sv.skill_md.encode("utf-8")
        info = tarfile.TarInfo(name=f"{name}/SKILL.md")
        info.size = len(md_bytes)
        tar.addfile(info, io.BytesIO(md_bytes))
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/gzip",
        as_attachment=True,
        download_name=f"{name}-{sv.version}.tar.gz",
    )


# ── POST /api/skills ──────────────────────────────────────────────────────────
@skills_bp.route("", methods=["POST"])
def push_skill():
    """上傳（push）新的 Skill Bundle。
    
    支援兩種方式：
    1. JSON body（含 skill_md 欄位）
    2. multipart/form-data（上傳 .tar.gz 檔案）
    """
    # --- JSON mode ---
    if request.is_json:
        data = request.get_json()
        required = ["name", "version", "description", "author", "skill_md"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        skill = Skill.query.filter_by(name=data["name"]).first()
        if not skill:
            skill = Skill(
                name=data["name"],
                description=data["description"],
                author=data["author"],
                license=data.get("license", "MIT"),
                repository=data.get("repository"),
                tags=data.get("tags", []),
            )
            db.session.add(skill)
        else:
            skill.description = data["description"]
            skill.tags = data.get("tags", skill.tags)

        existing_version = SkillVersion.query.filter_by(
            skill_id=skill.id, version=data["version"]
        ).first()
        if existing_version:
            return jsonify({"error": f"Version {data['version']} already exists"}), 409

        skill.latest_version = data["version"]

        skill_md = data["skill_md"]
        checksum = hashlib.sha256(skill_md.encode()).hexdigest()

        sv = SkillVersion(skill=skill, version=data["version"], skill_md=skill_md, checksum=checksum)
        db.session.add(sv)
        db.session.commit()

        return jsonify({"message": "Skill published", "name": skill.name, "version": sv.version}), 201

    # --- File upload mode ---
    if "bundle" not in request.files:
        return jsonify({"error": "No bundle file provided"}), 400

    file = request.files["bundle"]
    meta = request.form

    required_meta = ["name", "version", "description", "author"]
    missing = [f for f in required_meta if not meta.get(f)]
    if missing:
        return jsonify({"error": f"Missing form fields: {missing}"}), 400

    # Save bundle
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    bundle_filename = f"{meta['name']}-{meta['version']}.tar.gz"
    bundle_path = os.path.join(UPLOAD_DIR, bundle_filename)
    file.save(bundle_path)

    # Compute checksum
    with open(bundle_path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    # Extract SKILL.md from bundle
    skill_md = ""
    try:
        with tarfile.open(bundle_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("SKILL.md"):
                    f = tar.extractfile(member)
                    if f:
                        skill_md = f.read().decode("utf-8")
                    break
    except Exception as e:
        return jsonify({"error": f"Invalid bundle: {e}"}), 400

    skill = Skill.query.filter_by(name=meta["name"]).first()
    if not skill:
        skill = Skill(
            name=meta["name"],
            description=meta["description"],
            author=meta["author"],
            license=meta.get("license", "MIT"),
            repository=meta.get("repository"),
            tags=meta.get("tags", "").split(",") if meta.get("tags") else [],
        )
        db.session.add(skill)

    skill.latest_version = meta["version"]
    sv = SkillVersion(
        skill=skill,
        version=meta["version"],
        skill_md=skill_md,
        bundle_path=bundle_path,
        checksum=checksum,
    )
    db.session.add(sv)
    db.session.commit()

    return jsonify({"message": "Skill published", "name": skill.name, "version": sv.version, "checksum": checksum}), 201
