"""Shared Rich formatting helpers."""
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
err = Console(stderr=True)


def success(msg: str) -> None:
    console.print(f"[green]✓[/green] {msg}")


def error(msg: str) -> None:
    err.print(f"[red]✗[/red] {msg}")


def info(msg: str) -> None:
    console.print(f"[dim]{msg}[/dim]")


def make_table(*headers: str) -> Table:
    t = Table(box=box.SIMPLE_HEAD, show_edge=False, header_style="bold cyan")
    for h in headers:
        t.add_column(h)
    return t
