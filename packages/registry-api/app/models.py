from datetime import datetime, timezone
from app import db


class Skill(db.Model):
    """A published Agent Skill."""

    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    license = db.Column(db.String(50), default="MIT")
    repository = db.Column(db.String(500))
    tags = db.Column(db.JSON, default=list)
    category = db.Column(db.String(50), nullable=True, index=True)  # 技能分類
    downloads = db.Column(db.Integer, default=0)
    latest_version = db.Column(db.String(20), default="1.0.0")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    versions = db.relationship(
        "SkillVersion", backref="skill", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, detail=False):
        # 輔助函式：確保日期屬性正確序列化
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)

        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "owner_id": self.owner_id,
            "license": self.license,
            "repository": self.repository,
            "tags": self.tags or [],
            "category": self.category,
            "downloads": self.downloads,
            "latest_version": self.latest_version,
            "created_at": format_date(self.created_at),
            "updated_at": format_date(self.updated_at),
        }
        if detail and self.versions:
            # 輔助函式：確保 max() 比較時型別一致
            def get_published_at(v):
                val = v.published_at or datetime.min
                # 如果 SQLite 傳回字串而 datetime.min 是 datetime 物件，會報錯
                # 這裡統一轉為字串比較或確保皆為 datetime
                return str(val) if not hasattr(val, "isoformat") else val.isoformat()

            latest = max(self.versions, key=get_published_at)
            data["skill_md"] = latest.skill_md
            data["versions"] = [v.to_dict() for v in self.versions]
        return data


    def __repr__(self):
        return f"<Skill {self.name}@{self.latest_version}>"


class SkillVersion(db.Model):
    """A specific version of a Skill Bundle."""

    __tablename__ = "skill_versions"

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    skill_md = db.Column(db.Text, nullable=False)
    bundle_path = db.Column(db.String(500))  # path to stored .tar.gz
    checksum = db.Column(db.String(128))     # sha256 of bundle
    published_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("skill_id", "version", name="uq_skill_version"),
    )

    def to_dict(self):
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)

        return {
            "version": self.version,
            "published_at": format_date(self.published_at),
            "checksum": self.checksum,
        }

    def __repr__(self):
        return f"<SkillVersion {self.skill_id}@{self.version}>"


class User(db.Model):
    """Registry user / skill author."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_token_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default="user")  # admin, maintainer, user
    permissions = db.Column(db.JSON, default=list)   # e.g ["skill:create", "skill:delete"]
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    skills = db.relationship("Skill", backref="owner", lazy=True)

    def to_dict(self):
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "permissions": self.permissions or [],
            "created_at": format_date(self.created_at),
        }

    def __repr__(self):
        return f"<User {self.username}>"
