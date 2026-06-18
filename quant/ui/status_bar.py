"""QUANT CLI — /status dashboard (Space Cyberpunk)."""
from __future__ import annotations
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

C = {
    "text":         "#dce8ff",
    "text_muted":   "#6e6a85",
    "accent":       "#9d4edd",
    "accent_bright":"#bf5fff",
    "accent_dark":  "#6e40c9",
    "ai_cyan":      "#00f5d4",
    "success":      "#50fa7b",
    "error":        "#ff5555",
    "warning":      "#f1fa8c",
    "pink":         "#ff79c6",
    "orange":       "#ffb86c",
}

console = Console()


def print_status(provider_info: dict, mode: str = "chat") -> None:
    ram = psutil.virtual_memory()
    used_gb = ram.used / 1e9
    total_gb = ram.total / 1e9
    pct = ram.percent
    ram_color = C["success"] if pct < 70 else C["warning"] if pct < 90 else C["error"]

    try:
        cpu = psutil.cpu_percent(interval=0.3)
        cpu_color = C["success"] if cpu < 60 else C["warning"] if cpu < 85 else C["error"]
    except Exception:
        cpu, cpu_color = 0.0, C["success"]

    ctx = provider_info.get("context", 0)

    t = Table(box=None, show_header=False, padding=(0, 3))
    t.add_column(style=C["text_muted"], no_wrap=True, width=14)
    t.add_column(style=C["text"])

    t.add_row("Engine", f"[bold {C['accent_bright']}]{provider_info.get('provider', '—')}[/]")
    t.add_row("Model", f"[bold {C['text']}]{provider_info.get('model', '—')}[/]")
    t.add_row("Context", f"[bold {C['accent']}]{ctx // 1024}k[/] tokens")
    t.add_row("Mode", f"[bold {C['pink']}]{mode.upper()}[/]")
    t.add_row("RAM", f"[{ram_color}]{used_gb:.1f} / {total_gb:.1f} GB ({pct}%)[/]")
    t.add_row("CPU", f"[{cpu_color}]{cpu:.0f}%[/]")

    console.print(Panel(
        t, title=f"[bold {C['accent_bright']}]◈ QUANT STATUS ◈[/]",
        border_style=C["accent_dark"], padding=(1, 2), box=box.ROUNDED,
    ))
