"""登出指令。"""
import click
from agentskills.api_client import logout as do_logout

@click.command()
def logout():
    """從 Registry 登出並清除本地 Token。"""
    do_logout()
    click.echo("✅ 已成功登出，本地 Token 已清除。")
