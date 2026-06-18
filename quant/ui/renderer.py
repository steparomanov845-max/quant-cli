"""QUANT CLI — Renderer (Space Cyberpunk edition)."""
from __future__ import annotations
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.rule import Rule
from rich.table import Table
from rich import box
from rich.align import Align


C = {
    "bg":           "#0f0a19",
    "bg_panel":     "#0d0117",
    "text":         "#dce8ff",
    "text_dim":     "#7209b7",
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
    "blue":         "#8be9fd",
    "nebula1":      "#4c1d95",
    "nebula2":      "#7c3aed",
}

QUANT_THEME = Theme({
    "quant.brand":     f"bold {C['accent_bright']}",
    "quant.user":      f"bold {C['text']}",
    "quant.assistant": C["ai_cyan"],
    "quant.tool":      f"bold {C['pink']}",
    "quant.error":     f"bold {C['error']}",
    "quant.dim":       C["text_muted"],
    "quant.success":   C["success"],
    "quant.warning":   C["warning"],
    "quant.border":    C["accent_dark"],
    "quant.accent":    C["accent"],
})

console = Console(theme=QUANT_THEME, highlight=True)

MODE_ICONS = {
    "chat": "◆", "agent": "⚡", "debug": "🔧",
    "arch": "🏗", "refactor": "♻", "research": "🔬",
}

MODE_COLORS = {
    "chat": C["accent_bright"], "agent": C["pink"], "debug": C["orange"],
    "arch": C["blue"], "refactor": C["success"], "research": C["warning"],
}

GRADIENT = ["#4c1d95", "#6d28d9", "#7c3aed", "#8b5cf6", "#a855f7", "#bf5fff"]

BANNER_ART = [
    "  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗",
    " ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝",
    " ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ",
    " ██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ",
    " ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ",
    "  ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝  ",
]

SLOGAN = "Your AI. Your Rules. Your Data stays with you."


def _hr(color: str = "") -> None:
    c = color or C["accent_dark"]
    console.print(Rule(style=c))


def print_banner() -> None:
    console.print()
    for i, line in enumerate(BANNER_ART):
        color = GRADIENT[min(i, len(GRADIENT) - 1)]
        console.print(f"  [{color}]{line}[/]")
    console.print()
    _hr()
    t = Text()
    t.append("  ◆ CLI 3.0", style=f"bold {C['accent_bright']}")
    t.append("  │  ", style=C["accent_dark"])
    t.append(SLOGAN, style=C["text_muted"])
    console.print(t)
    _hr()
    console.print()


def splash_animation(model: str = "", ctx: int = 0) -> None:
    from quant.ui.i18n import t
    model_short = model.split("/")[-1][:30] if model else "unknown"
    ctx_k = f"{ctx // 1024}k" if ctx else "?"

    steps = [
        (t("splash_init"), 0.0),
        (t("splash_tools"), 0.0),
        (t("splash_connect"), 0.0),
        (t("splash_model"), 0.0),
        (t("splash_context"), 0.0),
        (t("splash_safety"), 0.0),
        (t("splash_ready"), 0.0),
    ]

    console.print()
    for i, (label, delay) in enumerate(steps):
        pct = int((i + 1) / len(steps) * 100)
        filled = int(20 * pct / 100)
        empty = 20 - filled
        bar = f"[{C['nebula2']}]{'█' * filled}[/][{C['nebula1']}]{'░' * empty}[/]"

        if i < len(steps) - 1:
            spinner = ["⠋", "⠙", "⠹", "⠸"][i % 4]
            line = f"  [{C['text_muted']}]{spinner}[/]  {bar}  [{C['text_muted']}]{label}[/]"
        else:
            line = (
                f"  [{C['success']}]✓[/]  {bar}  [bold {C['success']}]{label}[/]\n"
                f"\n"
                f"  [{C['text_muted']}]{t('splash_model_label')}[/]  [bold {C['text']}]{model_short}[/]\n"
                f"  [{C['text_muted']}]{t('splash_ctx_label')}[/]    [bold {C['accent']}]{ctx_k}[/] {t('splash_tokens')}\n"
            )

        console.print(line)

    _hr()
    console.print()


def print_session_summary(
    duration: str = "",
    tool_calls: int = 0,
    backups: int = 0,
    tokens: int = 0,
    status: str = "",
) -> None:
    from quant.ui.i18n import t
    console.print()
    _hr(C["accent_bright"])

    title = Text()
    title.append(f"  {t('summary_title')}", style=f"bold {C['accent_bright']}")
    console.print(title)
    console.print(f"  {'─' * 42}")

    stats = [
        (t("summary_runtime"), duration or "unknown"),
        (t("summary_tools"), str(tool_calls)),
        (t("summary_backups"), str(backups)),
        (t("summary_tokens"), f"{tokens:,}" if tokens else "unknown"),
        (t("summary_status"), status or t("summary_completed")),
    ]

    for label, value in stats:
        console.print(f"  [{C['text_muted']}]{label:<22}[/] [bold white]{value}[/]")

    _hr(C["accent_bright"])
    console.print()


def print_user(message: str) -> None:
    console.print()
    console.print(f"  [{C['accent_dark']}]╭─ YOU ─{'─' * 36}[/]")
    for line in message.split("\n"):
        console.print(f"  [{C['accent_dark']}]│[/]  [bold {C['text']}]{line}[/]")
    console.print(f"  [{C['accent_dark']}]╰{'─' * 43}[/]")


def print_thinking(model: str = "") -> None:
    label = model.split("/")[-1][:24] if model else "QUANT"
    with console.status(
        f"  [{C['ai_cyan']}]◆[/] [{C['text_muted']}]{label} is thinking...[/]",
        spinner="dots"
    ):
        pass


def print_assistant(message: str, mode: str = "chat", model_name: str = "") -> None:
    color = MODE_COLORS.get(mode, C["accent_bright"])
    label = model_name.split("/")[-1][:30] if model_name else "QUANT"
    console.print()
    try:
        md = Markdown(message)
        console.print(Panel(
            md, border_style=color,
            title=f"[bold {C['ai_cyan']}]✦ {label}[/]",
            title_align="left", padding=(1, 2), box=box.ROUNDED,
        ))
    except Exception:
        console.print(Panel(
            message, border_style=color,
            title=f"[bold {C['ai_cyan']}]✦ {label}[/]",
            title_align="left", padding=(1, 2), box=box.ROUNDED,
        ))


def print_step(step: int, text: str) -> None:
    console.print(f"\n  [bold {C['accent_dark']}]Step {step}[/] [{C['text_muted']}]▸[/] [{C['text']}]{text}[/]")


def print_tool_call(tool_name: str, args: dict) -> None:
    args_parts = []
    for k, v in list(args.items())[:4]:
        val = str(v)[:60] + "…" if len(str(v)) > 60 else str(v)
        args_parts.append(f"[{C['text_muted']}]{k}[/]=[bold {C['pink']}]{val!r}[/]")
    args_str = "  ".join(args_parts)
    console.print(f"\n  [{C['accent_dark']}]┌─[/] [bold {C['pink']}]⚡ {tool_name}[/]")
    if args_str:
        console.print(f"  [{C['accent_dark']}]│[/]  {args_str}")


def print_tool_result(tool_name: str, result, success: bool) -> None:
    icon = "✓" if success else "✗"
    color = C["success"] if success else C["error"]
    if hasattr(result, "data") and result.data:
        data = result.data
        interesting = {k: v for k, v in data.items() if k not in ("diff",) and v is not None}
        preview = "  ".join(
            f"[{C['text_muted']}]{k}:[/] [white]{str(v)[:50]}[/]"
            for k, v in list(interesting.items())[:4]
        )
    else:
        preview = str(result)[:120]
    console.print(f"  [{C['accent_dark']}]└[/] [{color}]{icon} {tool_name}[/]  {preview}")


def print_context_bar(used: int, total: int, model: str = "", mode: str = "chat") -> None:
    if total <= 0:
        return
    pct = min(used / total * 100, 100)
    color = C["ai_cyan"] if pct < 60 else C["warning"] if pct < 85 else C["error"]
    filled = int(18 * pct / 100)
    bar = "█" * filled + "░" * (18 - filled)
    label = model.split("/")[-1][:20] if model else ""
    console.print(
        f"  [{C['text_muted']}]ctx[/] [{color}]{bar}[/] [{color}]{used:,}[/]"
        f"[{C['text_muted']}]/{total:,} ({pct:.0f}%)[/]  "
        f"[{C['text_muted']}]model[/] [white]{label}[/]"
    )


def print_error(message: str) -> None:
    console.print(Panel(
        f"[bold {C['error']}]{message}[/]",
        border_style=C["error"], title=f"[bold {C['error']}]ERROR[/]",
        title_align="left", padding=(0, 2), box=box.ROUNDED,
    ))


def print_warning(message: str) -> None:
    console.print(Panel(
        f"[bold {C['warning']}]{message}[/]",
        border_style=C["warning"], title=f"[bold {C['warning']}]WARNING[/]",
        title_align="left", padding=(0, 2), box=box.ROUNDED,
    ))


def print_info(message: str) -> None:
    console.print(f"  [{C['text_muted']}]{message}[/]")


def print_success(message: str) -> None:
    console.print(f"  [{C['success']}]✓[/]  {message}")


def print_mode_change(mode: str) -> None:
    icon = MODE_ICONS.get(mode, "◆")
    color = MODE_COLORS.get(mode, C["accent_bright"])
    console.print()
    _hr(color)
    t = Text()
    t.append(f"  {icon}  {mode.upper()}  {icon}", style=f"bold {color}")
    console.print(Align.center(t))
    _hr(color)
    console.print()


def print_provider_info(info: dict) -> None:
    model = info.get("model", "?")
    provider = info.get("provider", "?")
    ctx = info.get("context", 0) // 1024
    t = Table(box=None, show_header=False, padding=(0, 2))
    t.add_column(style=C["text_muted"], no_wrap=True)
    t.add_column(style=C["text"])
    t.add_row("provider", f"[bold {C['accent_bright']}]{provider}[/]")
    t.add_row("model", f"[bold {C['text']}]{model}[/]")
    t.add_row("context", f"[bold {C['accent']}]{ctx}k[/] tokens")
    console.print(Panel(t, border_style=C["accent_dark"], padding=(0, 2),
                        expand=False, box=box.ROUNDED))


def print_help(commands: dict) -> None:
    console.print()
    _hr()
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    t.add_column(style=f"bold {C['pink']}", no_wrap=True, width=20)
    t.add_column(style=C["text"])
    for cmd, desc in commands.items():
        t.add_row(cmd, desc)
    console.print(Panel(t, title=f"[bold {C['accent_bright']}]◆ COMMANDS[/]",
                        border_style=C["accent_dark"], box=box.ROUNDED))
    console.print()


def print_task_complete(summary: str = "") -> None:
    console.print()
    _hr(C["success"])
    console.print(f"  [{C['success']}]✓ Task completed[/]")
    if summary:
        console.print(f"  [{C['text_muted']}]{summary}[/]")
    _hr(C["success"])
    console.print()


def print_confirm_prompt(tool_name: str, args: dict) -> bool:
    console.print()
    desc = _get_action_description(tool_name, args)
    console.print(Panel(
        f"[bold {C['warning']}]{desc}[/]\n\n"
        f"[{C['text_muted']}]Details:[/]\n"
        f"{_format_args_preview(args)}",
        border_style=C["warning"],
        title=f"[bold {C['warning']}]CONFIRM ACTION[/]",
        title_align="left",
        padding=(1, 2),
        box=box.ROUNDED,
    ))
    try:
        answer = console.input(
            f"  [bold {C['warning']}]Execute?[/] [dim]([/]y[{C['text_muted']}]/[/]n[{C['text_muted']}])[/] "
            f"[bold {C['accent_dark']}]›[/] "
        ).strip().lower()
        return answer in ("y", "yes", "да", "д")
    except (KeyboardInterrupt, EOFError):
        return False


def _get_action_description(tool_name: str, args: dict) -> str:
    if tool_name == "WRITE_FILE":
        path = args.get("path", "?")
        lines = args.get("lines", "?")
        return f"Write file: {path} ({lines} lines)"
    elif tool_name == "EDIT_FILE":
        path = args.get("path", "?")
        return f"Edit file: {path}"
    elif tool_name == "CMD":
        cmd = args.get("command", "?")[:80]
        return f"Run command: {cmd}"
    elif tool_name == "FILESYSTEM":
        action = args.get("action", "?")
        path = args.get("path", "?")
        if action == "delete":
            return f"Delete: {path}"
        elif action == "move":
            return f"Move: {path} -> {args.get('dest', '?')}"
        return f"Filesystem: {action} {path}"
    return f"Execute: {tool_name}"


def _format_args_preview(args: dict) -> str:
    lines = []
    for k, v in args.items():
        val = str(v)
        if len(val) > 120:
            val = val[:120] + "..."
        lines.append(f"  [{C['text_muted']}]{k}[/]: [{C['text']}]{val}[/]")
    return "\n".join(lines) if lines else f"  [{C['text_muted']}](no args)[/]"
