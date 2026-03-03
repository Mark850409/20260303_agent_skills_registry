"""agentskills search - 搜尋平台上的 Skills。"""
import click
from rich.console import Console
from rich.table import Table
from rich import box
import agentskills.api_client as api

console = Console()


@click.command()
@click.argument("keyword", default="")
@click.option("--tag", "-t", default="", help="依標籤篩選")
@click.option("--page", "-p", default=1, help="頁碼")
def search_cmd(keyword: str, tag: str, page: int):
    """搜尋平台上的 Skills。

    \b
    範例:
      agentskills search "web search"
      agentskills search --tag productivity
    """
    try:
        result = api.search_skills(keyword, tags=tag, page=page)
    except Exception as e:
        console.print(f"[red]✗ 搜尋失敗: {e}[/red]")
        return

    skills = result.get("skills", [])
    total = result.get("total", 0)

    if not skills:
        console.print("[yellow]找不到符合的 Skills[/yellow]")
        return

    table = Table(box=box.ROUNDED, border_style="dim", show_header=True, header_style="bold green")
    table.add_column("名稱", style="bold white", min_width=20)
    table.add_column("描述", style="dim white", max_width=50)
    table.add_column("版本", style="green", justify="center")
    table.add_column("⬇ 下載", justify="right", style="dim")
    table.add_column("標籤", style="cyan")

    for s in skills:
        tags_str = " ".join(f"#{t}" for t in (s.get("tags") or [])[:4])
        table.add_row(
            s["name"],
            s["description"][:60] + ("…" if len(s["description"]) > 60 else ""),
            f"v{s['latest_version']}",
            str(s.get("downloads", 0)),
            tags_str,
        )

    console.print(f"\n[bold]找到 {total} 個 Skills[/bold]（第 {page} 頁）\n")
    console.print(table)
    console.print(f"\n安裝：[cyan]agentskills pull <name>[/cyan]")
