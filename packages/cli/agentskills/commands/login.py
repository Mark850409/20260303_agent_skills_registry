"""agentskills login - 登錄 Registry 並取得 Token。"""
import click
from rich.console import Console
import agentskills.api_client as api

console = Console()

@click.command()
def login_cmd():
    """登錄 Registry 以取得發布權限。"""
    console.print("[bold cyan]🔑 登錄 AgentSkills Registry[/bold cyan]")
    
    username = click.prompt("使用者名稱 (Username)")
    email = click.prompt("電子郵件 (Email)")
    
    try:
        token = api.login(username, email)
        api.save_token(token)
        console.print(f"\n[green]✓ 登錄成功！[/green] Token 已儲存至本地。")
        console.print(f"你的使用者名稱是: [bold]{username}[/bold]")
    except Exception as e:
        console.print(f"\n[red]✗ 登錄失敗: {e}[/red]")
