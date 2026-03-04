"""Seed 資料：建立官方範例 Skills。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Skill, SkillVersion, User
from datetime import datetime, timezone

SEED_SKILLS = [
    {
        "name": "web-search",
        "description": "讓 AI Agent 能夠執行網頁搜尋，獲取最新資訊",
        "author": "agentskills-team",
        "license": "MIT",
        "category": "productivity",
        "tags": ["search", "web", "productivity", "information"],
        "repository": "https://github.com/agentskills/skills",
        "version": "1.0.0",
        "skill_md": """---
name: "Web Search"
description: "讓 AI Agent 能夠執行網頁搜尋"
version: "1.0.0"
author: "agentskills-team"
tags: [search, web, productivity]
license: "MIT"
---

# Web Search Skill

This skill enables the AI agent to search the web for current information.

## When to Use

- When you need up-to-date information
- When the user asks about recent events
- When verifying facts from external sources

## Instructions

1. Formulate a precise search query
2. Execute the search using available tools
3. Synthesize results into a concise answer with citations
""",
    },
    {
        "name": "code-reviewer",
        "description": "系統性程式碼審查：安全性、效能、最佳實踐",
        "author": "agentskills-team",
        "license": "MIT",
        "category": "coding",
        "tags": ["code", "review", "quality", "security"],
        "repository": "https://github.com/agentskills/skills",
        "version": "1.0.0",
        "skill_md": """---
name: "Code Reviewer"
description: "系統性程式碼審查技能"
version: "1.0.0"
author: "agentskills-team"
tags: [code, review, quality, security]
license: "MIT"
---

# Code Reviewer Skill

Perform systematic code reviews covering security, performance, and best practices.

## Review Checklist

- **Security**: Input validation, SQL injection, XSS, authentication
- **Performance**: Algorithm complexity, database queries, caching opportunities
- **Maintainability**: Code clarity, naming conventions, documentation
- **Testing**: Test coverage, edge cases, mocking strategies

## Output Format

Provide feedback as:
1. **Critical** issues (must fix)
2. **Major** issues (should fix)
3. **Minor** suggestions (nice to have)
""",
    },
    {
        "name": "git-workflow",
        "description": "Git 工作流程最佳實踐與自動化工具",
        "author": "agentskills-team",
        "license": "MIT",
        "category": "devops",
        "tags": ["git", "workflow", "devops", "automation"],
        "repository": "https://github.com/agentskills/skills",
        "version": "1.0.0",
        "skill_md": """---
name: "Git Workflow"
description: "Git 操作最佳實踐"
version: "1.0.0"
author: "agentskills-team"
tags: [git, workflow, devops]
license: "MIT"
---

# Git Workflow Skill

Best practices for Git operations and branching strategies.

## Branching Strategy

- `main` / `master`: Production-ready code only
- `develop`: Integration branch
- `feature/xxx`: New features
- `fix/xxx`: Bug fixes
- `release/x.y.z`: Release preparation

## Commit Message Format

```
<type>(<scope>): <subject>

<body>
```

Types: feat, fix, docs, style, refactor, test, chore
""",
    },
    {
        "name": "doc-writer",
        "description": "自動產生高品質技術文件、API 文件與 README",
        "author": "agentskills-team",
        "license": "MIT",
        "category": "writing",
        "tags": ["documentation", "writing", "api", "readme"],
        "repository": "https://github.com/agentskills/skills",
        "version": "1.0.0",
        "skill_md": """---
name: "Doc Writer"
description: "技術文件撰寫工具"
version: "1.0.0"
author: "agentskills-team"
tags: [documentation, writing, api]
license: "MIT"
---

# Doc Writer Skill

Generate high-quality technical documentation automatically.

## Supported Doc Types

- **README.md**: Project overview, installation, usage
- **API Reference**: Endpoints, parameters, examples
- **Architecture Docs**: System design, diagrams
- **Changelog**: Version history
""",
    },
    {
        "name": "test-generator",
        "description": "根據程式碼自動生成完整的單元測試與整合測試",
        "author": "agentskills-team",
        "license": "MIT",
        "category": "coding",
        "tags": ["testing", "tdd", "automation", "quality"],
        "repository": "https://github.com/agentskills/skills",
        "version": "1.0.0",
        "skill_md": """---
name: "Test Generator"
description: "自動生成單元測試"
version: "1.0.0"
author: "agentskills-team"
tags: [testing, tdd, automation, quality]
license: "MIT"
---

# Test Generator Skill

Automatically generate comprehensive unit and integration tests.

## Test Generation Strategy

1. Analyze function signatures and docstrings
2. Identify edge cases and boundary conditions
3. Generate happy-path tests
4. Generate error-case tests
5. Generate mock/stub requirements

## Supported Frameworks

- Python: pytest, unittest
- JavaScript: Jest, Vitest, Mocha
- Go: testing package
""",
    },
]


import hashlib

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def _migrate_add_columns(engine):
    """對現有 SQLite DB 補上新欄位（idempotent migration）。"""
    with engine.connect() as conn:
        # 取得 skills 表現有欄位名稱
        existing_cols = {
            row[1]
            for row in conn.execute(
                __import__('sqlalchemy').text("PRAGMA table_info(skills)")
            )
        }
        # 定義需要補上的欄位（欄位名 -> ALTER TABLE 語句）
        missing_ddl = {
            "category": "ALTER TABLE skills ADD COLUMN category VARCHAR(50)",
        }
        for col, ddl in missing_ddl.items():
            if col not in existing_cols:
                conn.execute(__import__('sqlalchemy').text(ddl))
                print(f"[MIGRATE] Added column: skills.{col}")
        conn.commit()


def seed():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        # 自動 Migration：對現有 DB 補上尚未存在的欄位
        _migrate_add_columns(db.engine)

        # 1. 建立管理員用戶
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin", 
                email="admin@example.com", 
                role="admin", 
                permissions=["*:*"]
            )
            admin.api_token_hash = _hash_token("admin-token-123")
            db.session.add(admin)
            print("[OK] Created Admin user: admin")
        
        # 2. 建立一個維護者用戶
        maintainer = User.query.filter_by(username="maintainer").first()
        if not maintainer:
            maintainer = User(
                username="maintainer", 
                email="maintainer@example.com", 
                role="maintainer", 
                permissions=["skill:create", "skill:update"]
            )
            maintainer.api_token_hash = _hash_token("maintainer-token-123")
            db.session.add(maintainer)
            print("[OK] Created Maintainer user: maintainer")

        db.session.flush()

        # 3. 建立技能並關聯管理員
        for data in SEED_SKILLS:
            existing = Skill.query.filter_by(name=data["name"]).first()
            if existing:
                print(f"[SKIP] {data['name']} already exists")
                continue

            skill = Skill(
                name=data["name"],
                description=data["description"],
                author=data["author"],
                license=data["license"],
                tags=data["tags"],
                repository=data["repository"],
                latest_version=data["version"],
                downloads=0,
                owner_id=admin.id,
                category=data.get("category"),
            )
            db.session.add(skill)
            db.session.flush()

            sv = SkillVersion(
                skill_id=skill.id,
                version=data["version"],
                skill_md=data["skill_md"],
            )
            db.session.add(sv)
            print(f"[OK] Seeded: {data['name']}@{data['version']}")

        db.session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    seed()
