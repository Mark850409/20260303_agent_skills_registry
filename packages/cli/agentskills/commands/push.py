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
        
    meta = yaml.safe_load(parts[1]) if parts[1].strip() else {}
    if not isinstance(meta, dict):
        meta = {}
    meta["skill_md"] = content
    return meta

def push_single_skill(skill_dir: Path, user_info: dict = None):
    """發布單一 Skill。"""
    skill_md_path = skill_dir / "SKILL.md"
    try:
        meta = parse_skill_md(skill_md_path)
    except Exception as e:
        console.print(f"[red]✗ 解析 {skill_dir.name} 失敗: {e}[/red]")
        return False

    # 自動補全缺失欄位
    if "name" not in meta:
        meta["name"] = skill_dir.name
    
    if "version" not in meta:
        meta["version"] = "1.0.0"
        console.print(f"[dim]提示: {meta['name']} 缺少版本，已自動設為 1.0.0[/dim]")

    if "author" not in meta:
        if user_info and user_info.get("username"):
            meta["author"] = user_info["username"]
        else:
            meta["author"] = "anonymous"
        console.print(f"[dim]提示: {meta['name']} 缺少作者，已自動設為 {meta['author']}[/dim]")

    if "description" not in meta:
        meta["description"] = f"Skill: {meta['name']}"

    console.print(f"[dim]正在發布 [bold]{meta['name']}@{meta['version']}[/bold]...[/dim]")
    
    try:
        api.push_skill(meta)
        console.print(f"[green]✓ {meta['name']} 發布成功！[/green]")
        return True
    except Exception as e:
        if "409" in str(e):
            console.print(f"[yellow]⚠ 版本衝突: {meta['name']}@{meta['version']} 已存在。[/yellow]")
        else:
            console.print(f"[red]✗ 發布 {meta['name']} 失敗: {e}[/red]")
        return False

@click.command()
@click.argument("path", default=".")
def push_cmd(path: str):
    """打包並發布 Skill 到 Registry。
    
    支援批量發布：若指定目錄不含 SKILL.md，將搜尋所有含 SKILL.md 的子目錄。
    """
    root_dir = Path(path)
    
    # 先獲取使用者資訊，用於補全作者
    user_info = None
    try:
        user_info = api.get_me()
    except:
        pass

    # 判斷是單一 Skill 還是批量
    skill_md_path = root_dir / "SKILL.md"
    if skill_md_path.exists():
        push_single_skill(root_dir, user_info)
    else:
        # 搜尋子目錄
        console.print(f"[dim]正在搜尋 {root_dir} 下的技能...[/dim]")
        found_skills = [p.parent for p in root_dir.glob("*/SKILL.md")]
        if not found_skills:
            console.print(f"[red]✗ 在 {root_dir} 或其子目錄中找不到任何 SKILL.md[/red]")
            return

        success_count = 0
        for skill_dir in found_skills:
            if push_single_skill(skill_dir, user_info):
                success_count += 1
        
        console.print(f"\n[green]ℹ 完成！成功發布 {success_count} 個技能。[/green]")

