"""agentskills login - 登錄 Registry 並取得 Token。"""
import click
from rich.console import Console
import agentskills.api_client as api

console = Console()

@click.command()
@click.option("--registry", help="Registry URL 網址 (預設使用現有的設定)")
def login_cmd(registry):
    """登錄 Registry 以取得發布權限。"""
    console.print("[bold cyan]🔑 登錄 AgentSkills Registry[/bold cyan]")
    
    current_registry = api.get_registry_url()
    registry_url = click.prompt("Registry URL", default=current_registry)
    if not registry_url:
        registry_url = current_registry

    username = click.prompt("使用者名稱 (Username)")
    password = click.prompt("密碼 (Password)", hide_input=True)
    
    try:
        api.save_config(registry_url=registry_url)
        token = api.login(username, password)
        api.save_token(token)
        console.print(f"\n[green]✓ 登錄成功！[/green] Token 與環境已儲存至本地。")
        console.print(f"你的使用者名稱是: [bold]{username}[/bold]")
        console.print(f"目前 Registry 是: [bold]{registry_url}[/bold]")
    except Exception as e:
        console.print(f"\n[red]✗ 登錄失敗: {e}[/red]")
