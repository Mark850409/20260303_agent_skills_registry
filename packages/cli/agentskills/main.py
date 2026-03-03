"""agentskills CLI 主程式。"""
import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option("1.0.0", prog_name="agentskills")
def cli():
    """🧠 AgentSkills — AI Agent Skills Registry CLI

    \b
    從 Registry 安裝:  agentskills pull web-search
    從 Git 安裝:       agentskills pull github:user/my-skills
    搜尋:              agentskills search "web search"
    發布:              agentskills push ./my-skill
    建立骨架:           agentskills init my-skill
    Vendor 鎖定:       agentskills vendor web-search@1.0.0
    """

from agentskills.commands.init import init_cmd
from agentskills.commands.pull import pull_cmd
from agentskills.commands.push import push_cmd
from agentskills.commands.search import search_cmd
from agentskills.commands.vendor import vendor_cmd
from agentskills.commands.login import login_cmd

cli.add_command(init_cmd, "init")
cli.add_command(pull_cmd, "pull")
cli.add_command(push_cmd, "push")
cli.add_command(search_cmd, "search")
cli.add_command(vendor_cmd, "vendor")
cli.add_command(login_cmd, "login")

if __name__ == "__main__":
    cli()
