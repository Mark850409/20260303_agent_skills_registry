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
    tags = fields.List(fields.String(), dump_default=list)
    downloads = fields.Integer(dump_only=True)
    latest_version = fields.String(dump_only=True)
    created_at = fields.String(dump_only=True)
    updated_at = fields.String(dump_only=True)
    skill_md = fields.String(dump_only=True)
    versions = fields.List(fields.Nested(SkillVersionSchema), dump_only=True)


class SkillQuerySchema(Schema):
    q = fields.String(load_default="")
    tags = fields.String(load_default="")
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
    tags = fields.List(fields.String(), load_default=list)
    skill_md = fields.String(required=True)


class AuthLoginSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)


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
    role = fields.String(load_default="user")
    permissions = fields.List(fields.String(), load_default=list)


class SkillUpdateSchema(Schema):
    description = fields.String()
    author = fields.String()
    license = fields.String()
    repository = fields.String()
    tags = fields.List(fields.String())


class UserUpdateSchema(Schema):
    username = fields.String()
    email = fields.String()
    role = fields.String()
    permissions = fields.List(fields.String())
