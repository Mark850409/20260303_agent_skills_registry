"""agentskills pull - 下載並安裝 Skills。"""
import os
import io
import shutil
import tarfile
import click
from pathlib import Path
from rich.console import Console
import agentskills.api_client as api
import agentskills.agents as agents
from git import Repo

console = Console()

def install_from_bytes(content: bytes, skill_name: str, target_dir: Path):
    """從 Registry 下載的 tar.gz 位元組安裝。"""
    target_dir.mkdir(parents=True, exist_ok=True)
    skill_path = target_dir / skill_name
    
    if skill_path.exists():
        shutil.rmtree(skill_path)
    
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
        # 由於 tar 裡面通常包含一個頂層目錄，我們要把內容解壓到 skill_path
        # 假設結構是 <name>/SKILL.md
        tar.extractall(path=target_dir)

def install_from_git(url: str, target_dir: Path, skill_dir: str = ""):
    """從 Git URL 安裝。"""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 建立臨時目錄
    tmp_path = Path(".agentskills-tmp")
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
        
    console.print(f"[dim]正在選取 Git 儲存庫: {url}...[/dim]")
    
    # Git URL 格式處理 (github:user/repo -> https://github.com/user/repo)
    clean_url = url
    if url.startswith("github:"):
        clean_url = f"https://github.com/{url.split(':', 1)[1]}"
    elif url.startswith("gitlab:"):
        clean_url = f"https://gitlab.com/{url.split(':', 1)[1]}"

    Repo.clone_from(clean_url, tmp_path)
    
    # 確定原始 Skill 目錄
    source_path = tmp_path
    if skill_dir:
        source_path = tmp_path / skill_dir
        if not source_path.exists():
            shutil.rmtree(tmp_path)
            raise ValueError(f"Git 儲存庫中找不到指定目錄: {skill_dir}")
            
    # 如果 source_path 下沒有 SKILL.md，給警告但繼續
    if not (source_path / "SKILL.md").exists():
        console.print("[yellow]⚠️  警告: 安裝路徑下找不到 SKILL.md，這可能不是一個有效的 Agent Skill。[/yellow]")

    # 確定目標名稱 (取 URL 最後一段或 dir 名稱)
    target_name = skill_dir if skill_dir else clean_url.split("/")[-1].replace(".git", "")
    final_path = target_dir / target_name
    
    if final_path.exists():
        shutil.rmtree(final_path)
        
    shutil.copytree(source_path, final_path)
    shutil.rmtree(tmp_path)
    return target_name

@click.command()
@click.argument("name_or_url")
@click.option("--version", "-v", help="指定版本（僅限 Registry）")
@click.option("--agent", "-a", help="指定目標 AI Agent (如 cursor, claude-code)")
@click.option("--global", "is_global", is_flag=True, help="安裝到全域技能目錄")
@click.option("--skill", "git_skill_dir", help="Git 儲存庫中的特定技能子目錄")
def pull_cmd(name_or_url: str, version: str, agent: str, is_global: bool, git_skill_dir: str):
    """下載並安裝 Skill。

    \b
    範例:
      agentskills pull web-search
      agentskills pull web-search@1.0.0
      agentskills pull github:user/skills --skill web-search
      agentskills pull https://github.com/user/my-skill.git --agent cursor
    """
    # 決定 Agent
    if not agent:
        detected = agents.detect_agents()
        agent = detected[0]
    
    try:
        install_path = agents.get_install_path(agent, is_global)
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        return

    # 判斷是 Registry 名稱還是 Git URL
    is_git = name_or_url.startswith(("http", "github:", "gitlab:", "git@"))
    
    try:
        if is_git:
            installed_name = install_from_git(name_or_url, install_path, git_skill_dir)
            console.print(f"[green]✓[/green] 已從 Git 安裝 [bold]{installed_name}[/bold] 到 [dim]{install_path}[/dim]")
        else:
            # Registry 安裝
            # 支援 name@version 語法
            pkg_name = name_or_url
            if "@" in name_or_url and not version:
                pkg_name, version = name_or_url.split("@", 1)
            
            console.print(f"[dim]正在從 Registry 下載 {pkg_name}...[/dim]")
            content = api.download_skill(pkg_name, version)
            install_from_bytes(content, pkg_name, install_path)
            console.print(f"[green]✓[/green] 已安裝 [bold]{pkg_name}[/bold] 到 [dim]{install_path}[/dim]")
            
    except Exception as e:
        console.print(f"[red]✗ 安裝失敗: {e}[/red]")
