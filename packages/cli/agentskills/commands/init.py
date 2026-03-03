"""agentskills init - 建立 Skill 骨架目錄。"""
import os
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

SKILL_MD_TEMPLATE = """\
---
name: "{name}"
description: "描述這個 Skill 的功能"
version: "1.0.0"
author: "{author}"
tags: [tag1, tag2]
license: "MIT"
---

# {name}

<!-- 在這裡撰寫 AI Agent 的操作指令 -->

## When to Use

描述何時啟用此技能。

## Instructions

1. 步驟一
2. 步驟二
3. 步驟三

## Examples

提供使用範例。
"""


@click.command()
@click.argument("name")
@click.option("--author", "-a", default="", help="作者名稱")
def init_cmd(name: str, author: str):
    """建立 Skill 骨架目錄結構。

    \b
    範例:
      agentskills init my-skill
      agentskills init my-skill --author my-name
    """
    skill_dir = Path(name)
    if skill_dir.exists():
        console.print(f"[red]✗ 目錄已存在: {name}[/red]")
        raise click.Abort()

    if not author:
        author = click.prompt("作者名稱", default=os.environ.get("USER", "anonymous"))

    # Create structure
    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references").mkdir()
    (skill_dir / "assets").mkdir()

    # Write SKILL.md
    (skill_dir / "SKILL.md").write_text(
        SKILL_MD_TEMPLATE.format(name=name, author=author),
        encoding="utf-8"
    )

    # Write .gitkeep
    for sub in ["scripts", "references", "assets"]:
        (skill_dir / sub / ".gitkeep").touch()

    console.print(Panel(
        f"[green]✓[/green] Skill 骨架已建立：[bold]{name}/[/bold]\n\n"
        f"  [dim]{name}/[/dim]\n"
        f"  [dim]├── SKILL.md[/dim]       ← 編輯這個檔案\n"
        f"  [dim]├── scripts/[/dim]\n"
        f"  [dim]├── references/[/dim]\n"
        f"  [dim]└── assets/[/dim]\n\n"
        f"完成後執行: [cyan]agentskills push ./{name}[/cyan]",
        title="🧩 AgentSkills Init",
        border_style="green",
    ))
