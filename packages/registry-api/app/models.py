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
    downloads = db.Column(db.Integer, default=0)
    latest_version = db.Column(db.String(20), default="1.0.0")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    versions = db.relationship(
        "SkillVersion", backref="skill", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, detail=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "repository": self.repository,
            "tags": self.tags or [],
            "downloads": self.downloads,
            "latest_version": self.latest_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if detail and self.versions:
            latest = max(self.versions, key=lambda v: v.published_at or datetime.min)
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
        return {
            "version": self.version,
            "published_at": self.published_at.isoformat() if self.published_at else None,
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User {self.username}>"
