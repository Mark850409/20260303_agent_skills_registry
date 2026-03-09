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
    examples = db.Column(db.JSON, default=list)  # 新增提示詞範例
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
            "examples": self.examples or [],
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
    password_hash = db.Column(db.String(255))
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


class MCPServer(db.Model):
    """A published MCP (Model Context Protocol) Server."""

    __tablename__ = "mcp_servers"

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), unique=True, nullable=False, index=True)
    display_name     = db.Column(db.String(200), nullable=False)
    description      = db.Column(db.Text, nullable=False)
    author           = db.Column(db.String(100), nullable=False)
    repository       = db.Column(db.String(500))
    # SSE / remote 連線 URL（Remote 類型使用）
    endpoint_url     = db.Column(db.String(500))
    # sse | stdio | http
    transport        = db.Column(db.String(20), default="sse")
    category         = db.Column(db.String(50), nullable=True, index=True)
    tags             = db.Column(db.JSON, default=list)
    # 提供的工具 [{name, description}]
    tools            = db.Column(db.JSON, default=list)
    # 本地啟動設定 [{type, command, image/package, env:[]}]
    local_config     = db.Column(db.JSON, default=list)
    installs         = db.Column(db.Integer, default=0)
    is_verified      = db.Column(db.Boolean, default=False)
    latest_version   = db.Column(db.String(20), default="1.0.0")
    license          = db.Column(db.String(50), default="MIT")
    owner_id         = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at       = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self, detail=False):
        def fmt(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)

        data = {
            "id":             self.id,
            "name":           self.name,
            "display_name":   self.display_name,
            "description":    self.description,
            "author":         self.author,
            "repository":     self.repository,
            "endpoint_url":   self.endpoint_url,
            "transport":      self.transport,
            "category":       self.category,
            "tags":           self.tags or [],
            "tools":          self.tools or [],
            "local_config":   self.local_config or [],
            "installs":       self.installs,
            "is_verified":    self.is_verified,
            "latest_version": self.latest_version,
            "license":        self.license,
            "owner_id":       self.owner_id,
            "created_at":     fmt(self.created_at),
            "updated_at":     fmt(self.updated_at),
        }
        return data

    def __repr__(self):
        return f"<MCPServer {self.name}>"


class DockerRepository(db.Model):
    """A managed Docker Repository in the Registry."""

    __tablename__ = "docker_repositories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": format_date(self.created_at),
            "updated_at": format_date(self.updated_at),
        }

    def __repr__(self):
        return f"<DockerRepository {self.name}>"

class NpmPackage(db.Model):
    """A managed NPM Package in the Registry."""

    __tablename__ = "npm_packages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": format_date(self.created_at),
            "updated_at": format_date(self.updated_at),
        }

    def __repr__(self):
        return f"<NpmPackage {self.name}>"

class PromptSetting(db.Model):
    """Configuration settings for the Prompt Generator."""

    __tablename__ = "prompt_settings"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True) # scenario, role, format, tone, constraint
    name = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(100), nullable=True) # Extraneous grouping for roles
    content = db.Column(db.Text, nullable=True) # Optional additional content or description
    is_active = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0) # For custom sorting
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)
        
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "group_name": self.group_name,
            "content": self.content,
            "is_active": self.is_active,
            "order_index": self.order_index,
            "created_at": format_date(self.created_at),
            "updated_at": format_date(self.updated_at),
        }

    def __repr__(self):
        return f"<PromptSetting {self.category}:{self.name}>"

class PromptKnowledge(db.Model):
    """Knowledge base for storing and sharing generated prompts."""

    __tablename__ = "prompt_knowledge"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prompt_content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True) # comma-separated tags
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # Optional for now
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        def format_date(dt):
            if dt is None: return None
            return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)
        
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "prompt_content": self.prompt_content,
            "tags": self.tags.split(",") if self.tags else [],
            "author_id": self.author_id,
            "is_public": self.is_public,
            "created_at": format_date(self.created_at),
            "updated_at": format_date(self.updated_at),
        }

    def __repr__(self):
        return f"<PromptKnowledge {self.title}>"
