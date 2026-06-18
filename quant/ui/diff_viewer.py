"""QUANT CLI — Visual Diff Engine."""
from __future__ import annotations
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns

console = Console()

def show_diff(diff_lines: list[str], path: str = "") -> bool:
    if not diff_lines:
        console.print("[dim]No changes detected.[/dim]")
        return False

    old_lines = []
    new_lines = []

    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("-"):
            old_lines.append(Text(line, style="red"))
        elif line.startswith("+"):
            new_lines.append(Text(line, style="green"))
        else:
            old_lines.append(Text(line, style="dim"))
            new_lines.append(Text(line, style="dim"))

    old_text = "\n".join(str(l) for l in old_lines) or "[dim](empty)[/dim]"
    new_text = "\n".join(str(l) for l in new_lines) or "[dim](empty)[/dim]"

    old_panel = Panel(old_text, title=f"[red]OLD[/red]  {path}", border_style="red", expand=True)
    new_panel = Panel(new_text, title=f"[green]NEW[/green]  {path}", border_style="green", expand=True)

    console.print()
    console.print(Columns([old_panel, new_panel]))

    answer = console.input("\n[bold yellow]Apply changes?[/bold yellow] [y/N] ").strip().lower()
    return answer == "y"


def print_diff_inline(diff_lines: list[str]) -> None:
    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            console.print(f"[dim]{line.rstrip()}[/dim]")
        elif line.startswith("@@"):
            console.print(f"[cyan]{line.rstrip()}[/cyan]")
        elif line.startswith("-"):
            console.print(f"[red]{line.rstrip()}[/red]")
        elif line.startswith("+"):
            console.print(f"[green]{line.rstrip()}[/green]")
        else:
            console.print(f"[dim]{line.rstrip()}[/dim]")
