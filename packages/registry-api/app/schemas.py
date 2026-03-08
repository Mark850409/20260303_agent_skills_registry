from marshmallow import Schema, fields


class SkillVersionSchema(Schema):
    version = fields.String(dump_only=True)
    published_at = fields.String(dump_only=True)
    checksum = fields.String(dump_only=True)


class SkillSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    author = fields.String(required=True)
    license = fields.String(dump_default="MIT")
    repository = fields.String()
    examples = fields.List(fields.String(), dump_default=list)
    tags = fields.List(fields.String(), dump_default=list)
    category = fields.String(allow_none=True)
    downloads = fields.Integer(dump_only=True)
    latest_version = fields.String(dump_only=True)
    created_at = fields.String(dump_only=True)
    updated_at = fields.String(dump_only=True)
    skill_md = fields.String(dump_only=True)
    versions = fields.List(fields.Nested(SkillVersionSchema), dump_only=True)


class SkillQuerySchema(Schema):
    q = fields.String(load_default="")
    tags = fields.String(load_default="")
    category = fields.String(load_default="")
    sort = fields.String(load_default="downloads")
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=20)


class SkillListResponseSchema(Schema):
    skills = fields.List(fields.Nested(SkillSchema))
    total = fields.Integer()
    page = fields.Integer()
    pages = fields.Integer()
    per_page = fields.Integer()


class TagSchema(Schema):
    tag = fields.String()
    count = fields.Integer()


class StatsSchema(Schema):
    total_skills = fields.Integer()
    total_downloads = fields.Integer()


class SkillPushSchema(Schema):
    name = fields.String(required=True)
    version = fields.String(required=True)
    description = fields.String(required=True)
    author = fields.String(required=True)
    license = fields.String(load_default="MIT")
    repository = fields.String()
    examples = fields.List(fields.String(), load_default=list)
    tags = fields.List(fields.String(), load_default=list)
    category = fields.String(allow_none=True, load_default=None)
    skill_md = fields.String(required=True)


class AuthLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


class AuthTokenSchema(Schema):
    api_token = fields.String(dump_only=True)
    username = fields.String(dump_only=True)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String()
    email = fields.String()
    role = fields.String()
    permissions = fields.List(fields.String())
    created_at = fields.String(dump_only=True)


class UserQuerySchema(Schema):
    q = fields.String(load_default="")
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=20)


class UserListResponseSchema(Schema):
    users = fields.List(fields.Nested(UserSchema))
    total = fields.Integer()
    page = fields.Integer()
    pages = fields.Integer()
    per_page = fields.Integer()


class UserCreateSchema(Schema):
    username = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    role = fields.String(load_default="user")
    permissions = fields.List(fields.String(), load_default=list)


class SkillUpdateSchema(Schema):
    description = fields.String()
    author = fields.String()
    license = fields.String()
    repository = fields.String()
    examples = fields.List(fields.String())
    tags = fields.List(fields.String())
    category = fields.String(allow_none=True)


class UserUpdateSchema(Schema):
    username = fields.String()
    email = fields.String()
    password = fields.String(load_only=True)
    role = fields.String()
    permissions = fields.List(fields.String())


# ── MCP Server Schemas ─────────────────────────────────────────────

class MCPToolSchema(Schema):
    name        = fields.String()
    description = fields.String()


class MCPLocalConfigItemSchema(Schema):
    type    = fields.String()          # docker | python | node
    command = fields.String()          # 完整執行指令
    image   = fields.String()          # docker image（docker 專用）
    package = fields.String()          # npm/pip package（node/python 專用）
    env     = fields.List(fields.String())  # 需要的環境變數名稱


class MCPSchema(Schema):
    id             = fields.Integer(dump_only=True)
    name           = fields.String(required=True)
    display_name   = fields.String(required=True)
    description    = fields.String(required=True)
    author         = fields.String(required=True)
    license        = fields.String(dump_default="MIT")
    repository     = fields.String()
    endpoint_url   = fields.String(allow_none=True, load_default=None)
    transport      = fields.String(dump_default="sse")
    category       = fields.String(allow_none=True)
    tags           = fields.List(fields.String(), dump_default=list)
    tools          = fields.List(fields.Nested(MCPToolSchema), dump_default=list)
    local_config   = fields.List(fields.Nested(MCPLocalConfigItemSchema), dump_default=list)
    installs       = fields.Integer(dump_only=True)
    is_verified    = fields.Boolean(dump_default=False)
    latest_version = fields.String(dump_only=True)
    owner_id       = fields.Integer(dump_only=True)
    created_at     = fields.String(dump_only=True)
    updated_at     = fields.String(dump_only=True)


class MCPQuerySchema(Schema):
    q          = fields.String(load_default="")
    category   = fields.String(load_default="")
    tags       = fields.String(load_default="")
    transport  = fields.String(load_default="")
    sort       = fields.String(load_default="installs")
    page       = fields.Integer(load_default=1)
    per_page   = fields.Integer(load_default=20)


class MCPListResponseSchema(Schema):
    mcps     = fields.List(fields.Nested(MCPSchema))
    total    = fields.Integer()
    page     = fields.Integer()
    pages    = fields.Integer()
    per_page = fields.Integer()


class MCPPublishSchema(Schema):
    name          = fields.String(required=True)
    display_name  = fields.String(required=True)
    description   = fields.String(required=True)
    author        = fields.String(required=True)
    license       = fields.String(load_default="MIT")
    repository    = fields.String()
    endpoint_url  = fields.String(allow_none=True, load_default=None)
    transport     = fields.String(load_default="sse")
    category      = fields.String(allow_none=True, load_default=None)
    tags          = fields.List(fields.String(), load_default=list)
    tools         = fields.List(fields.Dict(), load_default=list)
    local_config  = fields.List(fields.Dict(), load_default=list)
    latest_version = fields.String(load_default="1.0.0")


class MCPUpdateSchema(Schema):
    display_name  = fields.String()
    description   = fields.String()
    author        = fields.String()
    license       = fields.String()
    repository    = fields.String()
    endpoint_url  = fields.String(allow_none=True, load_default=None)
    transport     = fields.String()
    category      = fields.String(allow_none=True)
    tags          = fields.List(fields.String())
    local_config  = fields.List(fields.Dict())

# ── Docker Repository Schemas ──────────────────────────────────────

class DockerRepositorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)
    owner_id = fields.Integer(dump_only=True)
    created_at = fields.String(dump_only=True)
    updated_at = fields.String(dump_only=True)


class DockerRepositoryQuerySchema(Schema):
    q = fields.String(load_default="")
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=10)


class DockerRepositoryListResponseSchema(Schema):
    repositories = fields.List(fields.Nested(DockerRepositorySchema))
    total = fields.Integer()
    page = fields.Integer()
    pages = fields.Integer()
    per_page = fields.Integer()


class DockerRepositoryCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(allow_none=True)


class DockerRepositoryUpdateSchema(Schema):
    description = fields.String(allow_none=True)

# ── Npm Package Schemas ──────────────────────────────────────────────

class NpmPackageSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)
    owner_id = fields.Integer(dump_only=True)
    created_at = fields.String(dump_only=True)
    updated_at = fields.String(dump_only=True)


class NpmPackageQuerySchema(Schema):
    q = fields.String(load_default="")
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=10)


class NpmPackageListResponseSchema(Schema):
    packages = fields.List(fields.Nested(NpmPackageSchema))
    total = fields.Integer()
    page = fields.Integer()
    pages = fields.Integer()
    per_page = fields.Integer()


class NpmPackageCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(allow_none=True)


class NpmPackageUpdateSchema(Schema):
    description = fields.String(allow_none=True)
