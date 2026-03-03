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

def remove_readonly(func, path, _):
    """清除 Windows 唯讀屬性的回呼函式，用於 shutil.rmtree。"""
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def install_from_bytes(content: bytes, skill_name: str, target_dir: Path):
    """從 Registry 下載的 tar.gz 位元組安裝。"""
    target_dir.mkdir(parents=True, exist_ok=True)
    skill_path = target_dir / skill_name
    
    if skill_path.exists():
        shutil.rmtree(skill_path, onerror=remove_readonly)
    
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
        shutil.rmtree(tmp_path, onerror=remove_readonly)
        
    console.print(f"[dim]正在選取 Git 儲存庫: {url}...[/dim]")
    
    # Git URL 格式處理
    clean_url = url
    if url.startswith("github:"):
        clean_url = f"https://github.com/{url.split(':', 1)[1]}"
    elif url.startswith("gitlab:"):
        clean_url = f"https://gitlab.com/{url.split(':', 1)[1]}"

    try:
        Repo.clone_from(clean_url, tmp_path, depth=1)
    except Exception as e:
        if tmp_path.exists():
            shutil.rmtree(tmp_path, onerror=remove_readonly)
        raise e
    
    # 邏輯優化：偵測來源路徑
    source_path = tmp_path
    
    # 如果使用者指定了 --skill 子目錄
    if skill_dir:
        source_path = tmp_path / skill_dir
        if not source_path.exists():
            # 嘗試在 skills/ 下找
            if (tmp_path / "skills" / skill_dir).exists():
                source_path = tmp_path / "skills" / skill_dir
            else:
                shutil.rmtree(tmp_path, onerror=remove_readonly)
                raise ValueError(f"Git 儲存庫中找不到指定目錄: {skill_dir}")
    
    # 自動偵測：如果根目錄沒有 SKILL.md 但有 skills/ 目錄，且裡面只有一個目錄，或者是想要拉取整個內容
    elif not (tmp_path / "SKILL.md").exists():
        if (tmp_path / "skills").is_dir():
            # 這裡不自動進入，除非我們確定目標。
            # 但使用者反映多了一層，是因為我們把含有多個技能的 'skills' 目錄整層拷貝過去了。
            source_path = tmp_path / "skills"
            console.print("[dim]提示: 偵測到 Monorepo 結構，將從 'skills/' 目錄安裝。[/dim]")

    # 確定目標名稱：如果 source_path 是臨時目錄下的某個子目錄，取該子目錄名。
    # 如果 source_path 就是 tmp_path，取倉庫名。
    if skill_dir:
        target_name = skill_dir
    elif source_path.name != ".agentskills-tmp":
        target_name = source_path.name
    else:
        target_name = clean_url.split("/")[-1].replace(".git", "")

    # 如果目標路徑下原本就有東西，先清除
    final_path = target_dir / target_name
    if final_path.exists():
        shutil.rmtree(final_path, onerror=remove_readonly)
        
    # 關鍵修正：如果是要安裝「多個技能」到技能目錄，我們應該遍歷複製，而不是把父目錄拷貝進去。
    # 但這裡的設計是 pull 一個「技能」。如果 source_path 下面是一堆技能子目錄（且沒有 SKILL.md），
    # 我們應該把那些子目錄分別拷貝到 target_dir。
    
    if not (source_path / "SKILL.md").exists() and any(p.is_dir() and (p / "SKILL.md").exists() for p in source_path.iterdir()):
        # 這是一個「技能集合」目錄，我們將所有子技能拷貝到 target_dir
        count = 0
        for item in source_path.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                dest = target_dir / item.name
                if dest.exists():
                    shutil.rmtree(dest, onerror=remove_readonly)
                shutil.copytree(item, dest)
                count += 1
        shutil.rmtree(tmp_path, onerror=remove_readonly)
        return f"{count} 個技能 (來自 {target_name})"
    else:
        # 單一技能安裝
        shutil.copytree(source_path, final_path)
        
    if not (final_path / "SKILL.md").exists():
        console.print("[yellow]⚠️  警告: 安裝路徑下找不到 SKILL.md，這可能不是一個有效的 Agent Skill。[/yellow]")

    shutil.rmtree(tmp_path, onerror=remove_readonly)
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
