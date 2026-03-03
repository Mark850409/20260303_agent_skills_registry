"""agentskills push - 打包並發布 Skill 到 Registry。"""
import os
import io
import tarfile
import click
import yaml
from pathlib import Path
from rich.console import Console
import agentskills.api_client as api

console = Console()

def parse_skill_md(path: Path) -> dict:
    """解析 SKILL.md 的 YAML frontmatter。"""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError("SKILL.md 缺少 YAML frontmatter (---)")
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md YAML 格式錯誤")
        
    meta = yaml.safe_load(parts[1])
    meta["skill_md"] = content
    return meta

@click.command()
@click.argument("path", default=".")
def push_cmd(path: str):
    """打包並發布 Skill 到 Registry。

    \b
    範例:
      agentskills push .
      agentskills push ./my-skill
    """
    skill_dir = Path(path)
    skill_md_path = skill_dir / "SKILL.md"
    
    if not skill_md_path.exists():
        console.print(f"[red]✗ 在 {skill_dir} 中找不到 SKILL.md[/red]")
        return

    try:
        meta = parse_skill_md(skill_md_path)
    except Exception as e:
        console.print(f"[red]✗ 解析失敗: {e}[/red]")
        return

    # Verify required fields in YAML
    required = ["name", "version", "description", "author"]
    missing = [f for f in required if f not in meta]
    if missing:
        console.print(f"[red]✗ SKILL.md 缺少必要欄位: {missing}[/red]")
        return

    console.print(f"[dim]正在發布 [bold]{meta['name']}@{meta['version']}[/bold]...[/dim]")
    
    try:
        # TODO: 未來可以改為上傳 tar.gz 以包含 scripts/ 等目錄
        # 目前 API 支援直接傳送 JSON Payload
        api.push_skill(meta)
        console.print(f"[green]✓ 發布成功！[/green] 造訪 http://localhost:5173/skills/{meta['name']} 查看。")
    except Exception as e:
        if "409" in str(e):
            console.print(f"[yellow]⚠ 版本衝突: {meta['name']}@{meta['version']} 已經存在於 Registry。[/yellow]")
            console.print("[dim]提示: 請修改 SKILL.md 中的 version 欄位 (例如改為 1.0.1) 後再試。[/dim]")
        elif "401" in str(e):
            console.print(f"[red]✗ 發布失敗: {e}[/red]")
            console.print("[yellow]提示: 請先執行 `agentskills login`[/yellow]")
        else:
            console.print(f"[red]✗ 發布失敗: {e}[/red]")
