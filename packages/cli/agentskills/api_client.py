"""Registry API 客戶端。"""
import os
import httpx
from pathlib import Path

CONFIG_PATH = Path.home() / ".agentskills" / "config"
def load_config() -> dict:
    c = {"registry_url": "http://localhost:5006"}
    if CONFIG_PATH.exists():
        for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                c[k.strip()] = v.strip()
    if os.environ.get("AGENTSKILLS_REGISTRY"):
        c["registry_url"] = os.environ.get("AGENTSKILLS_REGISTRY")
    return c

def get_registry_url() -> str:
    return load_config().get("registry_url", "http://localhost:5006").rstrip("/")

def get_token() -> str | None:
    token_env = os.environ.get("AGENTSKILLS_TOKEN")
    if token_env:
        return token_env
    return load_config().get("token")

def save_config(**kwargs):
    c = load_config()
    c.update(kwargs)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in c.items() if v]
    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def save_token(token: str):
    save_config(token=token)

def logout():
    save_config(token="")


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
    resp = httpx.get(f"{get_registry_url()}/api/skills", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_skill(name: str, version: str | None = None) -> dict:
    url = f"{get_registry_url()}/api/skills/{name}"
    if version:
        url += f"/{version}"
    resp = httpx.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


def download_skill(name: str, version: str | None = None) -> bytes:
    token = get_token()
    if not token:
        raise ValueError("請先執行 `agentskills login` 登入 Registry 以取得下載權限。")
        
    url = f"{get_registry_url()}/api/skills/{name}"
    url += f"/{version}/download" if version else "/download"
    resp = httpx.get(url, headers=_headers(), timeout=60, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def push_skill(payload: dict) -> dict:
    token = get_token()
    if not token:
        raise ValueError("請先執行 `agentskills login` 登入 Registry 以取得發布權限。")

    resp = httpx.post(
        f"{get_registry_url()}/api/skills",
        json=payload,
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def login(username: str, email: str, registry_url: str = None) -> str:
    if registry_url:
        save_config(registry_url=registry_url)
    resp = httpx.post(
        f"{get_registry_url()}/api/auth/login",
        json={"username": username, "email": email},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["api_token"]


def get_me() -> dict:
    resp = httpx.get(
        f"{get_registry_url()}/api/auth/me",
        headers=_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
