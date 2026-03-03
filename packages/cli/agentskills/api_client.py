"""Registry API 客戶端。"""
import os
import httpx
from pathlib import Path

CONFIG_PATH = Path.home() / ".agentskills" / "config"
REGISTRY_URL = os.environ.get("AGENTSKILLS_REGISTRY", "http://localhost:5006")


def get_token() -> str | None:
    if CONFIG_PATH.exists():
        for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("token="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("AGENTSKILLS_TOKEN")


def save_token(token: str):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(f"token={token}\n", encoding="utf-8")


def logout():
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()


def _headers() -> dict:
    token = get_token()
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def search_skills(keyword: str, tags: str = "", page: int = 1) -> dict:
    params = {"q": keyword, "page": page, "per_page": 20}
    if tags:
        params["tags"] = tags
    resp = httpx.get(f"{REGISTRY_URL}/api/skills", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_skill(name: str, version: str | None = None) -> dict:
    url = f"{REGISTRY_URL}/api/skills/{name}"
    if version:
        url += f"/{version}"
    resp = httpx.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


def download_skill(name: str, version: str | None = None) -> bytes:
    token = get_token()
    if not token:
        raise ValueError("請先執行 `agentskills login` 登入 Registry 以取得下載權限。")
        
    url = f"{REGISTRY_URL}/api/skills/{name}"
    url += f"/{version}/download" if version else "/download"
    resp = httpx.get(url, headers=_headers(), timeout=60, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def push_skill(payload: dict) -> dict:
    token = get_token()
    if not token:
        raise ValueError("請先執行 `agentskills login` 登入 Registry 以取得發布權限。")

    resp = httpx.post(
        f"{REGISTRY_URL}/api/skills",
        json=payload,
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def login(username: str, email: str) -> str:
    resp = httpx.post(
        f"{REGISTRY_URL}/api/auth/login",
        json={"username": username, "email": email},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["api_token"]


def get_me() -> dict:
    resp = httpx.get(
        f"{REGISTRY_URL}/api/auth/me",
        headers=_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
