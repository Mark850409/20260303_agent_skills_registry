"""agentskills vendor - 鎖定並管理本地技能依賴。"""
import click
import json
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
import agentskills.api_client as api

console = Console()
LOCK_FILE = Path("agentskills.lock")
VENDOR_DIR = Path(".agentskills-vendor")

def load_lock():
    if LOCK_FILE.exists():
        return json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    return {"skills": {}}

def save_lock(data):
    LOCK_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

@click.command()
@click.argument("name", required=False)
@click.option("--remove", is_flag=True, help="移除指定技能")
def vendor_cmd(name: str, remove: bool):
    """管理本地技能依賴 (Vendoring)。
    
    不帶參數則根據 agentskills.lock 還原所有技能。
    """
    lock_data = load_lock()
    
    if name:
        if remove:
            if name in lock_data["skills"]:
                del lock_data["skills"][name]
                shutil.rmtree(VENDOR_DIR / name, ignore_errors=True)
                save_lock(lock_data)
                console.print(f"[green]✓ 已移除 {name}[/green]")
            else:
                console.print(f"[yellow]技能 {name} 不在依賴清單中[/yellow]")
        else:
            # Add/Update vendor
            pkg_name = name
            version = None
            if "@" in name:
                pkg_name, version = name.split("@", 1)
            
            console.print(f"[dim]正在將 {pkg_name} 鎖定到專案...[/dim]")
            try:
                # 取得資訊與下載
                skill_info = api.get_skill(pkg_name, version)
                content = api.download_skill(pkg_name, version)
                
                # 寫入 vendor 目錄
                VENDOR_DIR.mkdir(exist_ok=True)
                target = VENDOR_DIR / pkg_name
                if target.exists():
                    shutil.rmtree(target)
                
                # 解壓 (簡易版，假設已經有 download 邏輯)
                # 這裡調用之前 pull 的邏輯輔助
                from agentskills.commands.pull import install_from_bytes
                install_from_bytes(content, pkg_name, VENDOR_DIR)
                
                # 更新 lock
                lock_data["skills"][pkg_name] = {
                    "version": skill_info["latest_version"] if not version else version,
                    "checksum": skill_info.get("checksum", "")
                }
                save_lock(lock_data)
                console.print(f"[green]✓ 已鎖定 {pkg_name} 於 {VENDOR_DIR}/{pkg_name}[/green]")
            except Exception as e:
                console.print(f"[red]✗ 鎖定失敗: {e}[/red]")
    else:
        # Restore all from lock
        if not lock_data["skills"]:
            console.print("[yellow]目前沒有定義任何依賴項目。[/yellow]")
            return
            
        console.print(f"[bold]正在還原 {len(lock_data['skills'])} 個技能...[/bold]")
        for sname, info in lock_data["skills"].items():
            try:
                content = api.download_skill(sname, info["version"])
                from agentskills.commands.pull import install_from_bytes
                install_from_bytes(content, sname, VENDOR_DIR)
                console.print(f"  [green]✓[/green] {sname}@{info['version']}")
            except Exception as e:
                console.print(f"  [red]✗[/red] {sname}: {e}")
        console.print("\n[green]還原完成。[/green]")
