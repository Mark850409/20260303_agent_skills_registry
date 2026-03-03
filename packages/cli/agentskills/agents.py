"""Agent 識別名稱與全域/專案技能目錄對應表。"""
import os
import platform
from pathlib import Path

HOME = Path.home()

AGENTS = {
    "antigravity": {
        "name": "Antigravity",
        "global_dir": HOME / ".gemini" / "antigravity" / "skills",
        "project_dir": Path(".agents") / "skills",
    },
    "claude-code": {
        "name": "Claude Code",
        "global_dir": HOME / ".claude" / "skills",
        "project_dir": Path(".claude") / "skills",
    },
    "cursor": {
        "name": "Cursor",
        "global_dir": HOME / ".cursor" / "skills",
        "project_dir": Path(".cursor") / "skills",
    },
    "codex": {
        "name": "Codex",
        "global_dir": HOME / ".codex" / "skills",
        "project_dir": Path(".codex") / "skills",
    },
    "opencode": {
        "name": "OpenCode",
        "global_dir": HOME / ".opencode" / "skills",
        "project_dir": Path(".opencode") / "skills",
    },
    "github-copilot": {
        "name": "GitHub Copilot",
        "global_dir": HOME / ".github" / "copilot" / "skills",
        "project_dir": Path(".github") / "copilot" / "skills",
    },
    "roo": {
        "name": "Roo Code",
        "global_dir": HOME / ".roo" / "skills",
        "project_dir": Path(".roo") / "skills",
    },
}


def detect_agents() -> list[str]:
    """自動偵測目前環境中已安裝的 Agents。"""
    detected = []
    for agent_id, info in AGENTS.items():
        parent = info["global_dir"].parent
        if parent.exists():
            detected.append(agent_id)
    return detected or ["antigravity"]


def get_install_path(agent_id: str, is_global: bool = False) -> Path:
    """取得指定 Agent 的安裝路徑。"""
    agent = AGENTS.get(agent_id)
    if not agent:
        raise ValueError(f"未知的 Agent: {agent_id}。可用: {list(AGENTS.keys())}")
    return agent["global_dir"] if is_global else agent["project_dir"]
