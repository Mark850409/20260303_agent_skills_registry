"""後端 API 測試。"""
import pytest
import json
from app import create_app, db
from app.models import Skill, SkillVersion


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        _seed_test_data()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_test_data():
    skill = Skill(
        name="test-skill",
        description="A test skill",
        author="tester",
        tags=["test", "sample"],
        latest_version="1.0.0",
    )
    db.session.add(skill)
    db.session.flush()
    sv = SkillVersion(skill_id=skill.id, version="1.0.0", skill_md="---\nname: test\n---\n# Test")
    db.session.add(sv)
    db.session.commit()


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json["status"] == "ok"


class TestListSkills:
    def test_list_all(self, client):
        r = client.get("/api/skills")
        assert r.status_code == 200
        data = r.json
        assert "skills" in data
        assert data["total"] >= 1

    def test_search_by_name(self, client):
        r = client.get("/api/skills?q=test")
        assert r.status_code == 200
        assert any(s["name"] == "test-skill" for s in r.json["skills"])

    def test_search_no_result(self, client):
        r = client.get("/api/skills?q=nonexistent_xyz")
        assert r.status_code == 200
        assert r.json["total"] == 0


class TestGetSkill:
    def test_get_existing(self, client):
        r = client.get("/api/skills/test-skill")
        assert r.status_code == 200
        assert r.json["name"] == "test-skill"
        assert "skill_md" in r.json

    def test_get_missing(self, client):
        r = client.get("/api/skills/not-found")
        assert r.status_code == 404


class TestPushSkill:
    def test_push_new_skill(self, client):
        payload = {
            "name": "new-skill",
            "version": "1.0.0",
            "description": "A new skill",
            "author": "dev",
            "skill_md": "---\nname: new-skill\n---\n# New Skill",
            "tags": ["new"],
        }
        r = client.post("/api/skills", json=payload)
        assert r.status_code == 201
        assert r.json["name"] == "new-skill"

    def test_push_duplicate_version(self, client):
        payload = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "dup",
            "author": "tester",
            "skill_md": "---\nname: test\n---",
        }
        r = client.post("/api/skills", json=payload)
        assert r.status_code == 409


class TestTags:
    def test_list_tags(self, client):
        r = client.get("/api/skills/tags")
        assert r.status_code == 200
        assert isinstance(r.json, list)


class TestStats:
    def test_stats(self, client):
        r = client.get("/api/skills/stats")
        assert r.status_code == 200
        assert "total_skills" in r.json
