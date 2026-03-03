import os
import io
import hashlib
import tarfile
from flask import send_file, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app import db
from app.models import Skill, SkillVersion
from app.routes.auth import require_permission, get_current_user
from app.schemas import (
    SkillSchema, 
    SkillQuerySchema, 
    SkillListResponseSchema, 
    TagSchema, 
    StatsSchema,
    SkillPushSchema
)

skills_blp = Blueprint("skills", __name__, url_prefix="/api/skills", description="Operations on skills")

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "data/bundles")


@skills_blp.route("")
class Skills(MethodView):
    @skills_blp.arguments(SkillQuerySchema, location="query")
    @skills_blp.response(200, SkillListResponseSchema)
    def get(self, args):
        """搜尋 / 列出 Skills"""
        q = args.get("q", "").strip()
        tags_param = args.get("tags", "")
        sort = args.get("sort", "downloads")
        page = args.get("page", 1)
        per_page = args.get("per_page", 20)

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
                query = query.filter(Skill.tags.like(f'%"{tag}"%'))

        sort_map = {
            "downloads": Skill.downloads.desc(),
            "name": Skill.name.asc(),
            "created_at": Skill.created_at.desc(),
            "updated_at": Skill.updated_at.desc(),
        }
        query = query.order_by(sort_map.get(sort, Skill.downloads.desc()))

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "skills": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": per_page,
        }

    @skills_blp.arguments(SkillPushSchema)
    @skills_blp.response(201, SkillSchema)
    @require_permission("skill:create")
    def post(self, data):
        """上傳（push）新的 Skill Bundle (JSON)"""
        user = get_current_user()
        skill = Skill.query.filter_by(name=data["name"]).first()
        
        if not skill:
            skill = Skill(
                name=data["name"],
                description=data["description"],
                author=data["author"],
                license=data.get("license", "MIT"),
                repository=data.get("repository"),
                tags=data.get("tags", []),
                owner_id=user.id # Set owner
            )
            db.session.add(skill)
        else:
            # Check ownership for updates
            if user.role != "admin" and skill.owner_id != user.id:
                abort(403, message="You do not own this skill and cannot update it")
                
            skill.description = data["description"]
            skill.tags = data.get("tags", skill.tags)

        existing_version = SkillVersion.query.filter_by(
            skill_id=skill.id, version=data["version"]
        ).first()
        if existing_version:
            abort(409, message=f"Version {data['version']} already exists")

        skill.latest_version = data["version"]
        skill_md = data["skill_md"]
        checksum = hashlib.sha256(skill_md.encode()).hexdigest()

        sv = SkillVersion(skill=skill, version=data["version"], skill_md=skill_md, checksum=checksum)
        db.session.add(sv)
        db.session.commit()

        return skill


@skills_blp.route("/tags")
class Tags(MethodView):
    @skills_blp.response(200, TagSchema(many=True))
    def get(self):
        """列出所有標籤及統計數量"""
        skills = Skill.query.all()
        tag_counts = {}
        for skill in skills:
            for tag in (skill.tags or []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"tag": t, "count": c} for t, c in sorted_tags]


@skills_blp.route("/stats")
class Stats(MethodView):
    @skills_blp.response(200, StatsSchema)
    def get(self):
        """全站統計"""
        total_skills = Skill.query.count()
        total_downloads = db.session.query(db.func.sum(Skill.downloads)).scalar() or 0
        return {"total_skills": total_skills, "total_downloads": total_downloads}


@skills_blp.route("/<string:name>")
class SkillByName(MethodView):
    @skills_blp.response(200, SkillSchema)
    def get(self, name):
        """取得 Skill 詳情"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        return skill.to_dict(detail=True)


@skills_blp.route("/<string:name>/<string:version>")
class SkillVersionDetail(MethodView):
    @skills_blp.response(200, SkillSchema)
    def get(self, name, version):
        """取得特定版本詳情"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        sv = SkillVersion.query.filter_by(skill_id=skill.id, version=version).first_or_404()
        data = skill.to_dict()
        data["skill_md"] = sv.skill_md
        return data


@skills_blp.route("/<string:name>/download")
@skills_blp.route("/<string:name>/<string:version>/download")
class SkillDownload(MethodView):
    def get(self, name, version=None):
        """下載 Skill Bundle tar.gz"""
        skill = Skill.query.filter_by(name=name).first_or_404()
        if version:
            sv = SkillVersion.query.filter_by(skill_id=skill.id, version=version).first_or_404()
        else:
            sv = (
                SkillVersion.query.filter_by(skill_id=skill.id)
                .order_by(SkillVersion.published_at.desc())
                .first_or_404()
            )

        skill.downloads += 1
        db.session.commit()

        if sv.bundle_path and os.path.exists(sv.bundle_path):
            return send_file(
                sv.bundle_path,
                mimetype="application/gzip",
                as_attachment=True,
                download_name=f"{name}-{sv.version}.tar.gz",
            )

        # Re-generate from skill_md
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
