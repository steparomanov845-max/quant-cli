"""QUANT 3.0 — Space Cyberpunk TUI (Textual)."""
from __future__ import annotations
import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Static, Header, Footer, Input, RichLog, Label, Button, RadioSet
from textual.widgets._radio_button import RadioButton
from textual.reactive import reactive
from textual import work
from textual.binding import Binding
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box
from rich.align import Align


C = {
    "bg":           "#0f0a19",
    "bg_panel":     "#0d0117",
    "bg_status":    "#1a0a2e",
    "text":         "#dce8ff",
    "text_dim":     "#7209b7",
    "text_muted":   "#6e6a85",
    "accent":       "#9d4edd",
    "accent_bright":"#bf5fff",
    "accent_dark":  "#6e40c9",
    "ai_cyan":      "#00f5d4",
    "ai_cyan_dim":  "#00b4a0",
    "success":      "#50fa7b",
    "error":        "#ff5555",
    "warning":      "#f1fa8c",
    "pink":         "#ff79c6",
    "orange":       "#ffb86c",
    "blue":         "#8be9fd",
    "nebula1":      "#4c1d95",
    "nebula2":      "#7c3aed",
    "nebula3":      "#a855f7",
}


SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
GRADIENT = ["#4c1d95", "#6d28d9", "#7c3aed", "#8b5cf6", "#a855f7", "#bf5fff"]

_CONFIRM_FUT: asyncio.Future | None = None
_CONFIRM_RESULT = False
_CONFIRM_ALWAYS = False


def session_allow_all() -> bool:
    return _CONFIRM_ALWAYS


def set_session_allow(value: bool):
    global _CONFIRM_ALWAYS
    _CONFIRM_ALWAYS = value


def _get_confirm_display(tool_name: str, args: dict) -> str:
    if tool_name == "CMD":
        cmd = args.get("command", "?")
        return f"$ {cmd}"
    elif tool_name == "WRITE_FILE":
        path = args.get("path", "?")
        return str(path)
    elif tool_name == "EDIT_FILE":
        path = args.get("path", "?")
        return str(path)
    else:
        return " ".join(f"{k}={str(v)[:40]}" for k, v in list(args.items())[:3])


async def tui_confirm(tool_name: str, args: dict) -> bool:
    global _CONFIRM_ALWAYS, _CONFIRM_FUT, _CONFIRM_RESULT
    if _CONFIRM_ALWAYS:
        return True

    from quant.ui.tui import _get_tui_app
    app = _get_tui_app()
    if app is None:
        return True

    _CONFIRM_RESULT = False
    loop = asyncio.get_event_loop()
    _CONFIRM_FUT = loop.create_future()

    display = _get_confirm_display(tool_name, args)
    app._show_confirm_prompt(tool_name, display)
    result = await _CONFIRM_FUT
    app._hide_confirm_prompt()
    return result


class Sidebar(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = "unknown"
        self._provider = "lmstudio"
        self._host = "localhost:1234"
        self._dir = "."
        self._files = 0
        self._ctx_used = 0
        self._ctx_total = 32768
        self._mode = "chat"
        self._cpu = 0.0
        self._ram_used = 0.0
        self._ram_total = 0.0
        self._ram_pct = 0.0

    def update_info(self, model="", provider="", host="", dir="", files=0,
                    ctx_used=0, ctx_total=32768, mode="chat"):
        self._model = model
        self._provider = provider
        self._host = host
        self._dir = dir
        self._files = files
        self._ctx_used = ctx_used
        self._ctx_total = ctx_total
        self._mode = mode
        self.refresh()

    def update_system_stats(self):
        try:
            import psutil
            self._cpu = psutil.cpu_percent(interval=0)
            mem = psutil.virtual_memory()
            self._ram_used = mem.used / 1e9
            self._ram_total = mem.total / 1e9
            self._ram_pct = mem.percent
            self.refresh()
        except Exception:
            pass

    def _make_ctx_bar(self) -> Text:
        pct = min(self._ctx_used / self._ctx_total * 100, 100) if self._ctx_total > 0 else 0
        filled = int(16 * pct / 100)
        empty = 16 - filled

        if pct < 60:
            bar_color = C["ai_cyan"]
        elif pct < 85:
            bar_color = C["warning"]
        else:
            bar_color = C["error"]

        t = Text()
        t.append("┌" + "─" * 18 + "┐\n")
        t.append("│ ")
        t.append("█" * filled, style=bar_color)
        t.append("░" * empty, style=C["nebula1"])
        t.append(" │\n")
        t.append("└" + "─" * 18 + "┘\n")
        t.append(f"  {self._ctx_used:,} / {self._ctx_total:,}", style=C["text_muted"])
        t.append(f"\n  {pct:.1f}% used", style=bar_color)
        return t

    def render(self) -> Panel:
        t = Text()
        t.append("  ⚙ ENGINE\n", style=f"bold {C['accent']}")
        t.append(f"  {self._provider}\n", style=f"bold {C['text']}")
        t.append(f"  {self._host}\n\n", style=C["text_muted"])

        model_short = self._model.split("/")[-1][:22]
        t.append("  🧠 MODEL\n", style=f"bold {C['accent']}")
        t.append(f"  {model_short}\n\n", style=f"bold {C['ai_cyan']}")

        dir_short = self._dir[-28:] if len(self._dir) > 28 else self._dir
        t.append("  📂 PROJECT\n", style=f"bold {C['accent']}")
        t.append(f"  {dir_short}\n", style=C["text"])
        t.append(f"  {self._files} files tracked\n\n", style=C["text_muted"])

        t.append("  📊 CONTEXT\n", style=f"bold {C['accent']}")
        t.append_text(self._make_ctx_bar())

        if self._cpu > 0:
            cpu_color = C["success"] if self._cpu < 60 else C["warning"] if self._cpu < 85 else C["error"]
            ram_color = C["success"] if self._ram_pct < 70 else C["warning"] if self._ram_pct < 90 else C["error"]
            t.append("\n  💻 SYSTEM\n", style=f"bold {C['accent']}")
            t.append(f"  CPU  ", style=C["text_muted"])
            t.append(f"{self._cpu:.0f}%\n", style=cpu_color)
            t.append(f"  RAM  ", style=C["text_muted"])
            t.append(f"{self._ram_used:.1f}/{self._ram_total:.1f} GB\n", style=ram_color)
            ram_bar_filled = int(12 * self._ram_pct / 100)
            ram_bar_empty = 12 - ram_bar_filled
            t.append("  ", style=C["text_muted"])
            t.append("█" * ram_bar_filled, style=ram_color)
            t.append("░" * ram_bar_empty, style=C["nebula1"])
            t.append(f" {self._ram_pct:.0f}%\n", style=ram_color)

        if _CONFIRM_ALWAYS:
            t.append("\n  🛡 SECURITY\n", style=f"bold {C['warning']}")
            t.append(f"  Allow All", style=f"bold {C['warning']}")
        else:
            from quant.tools.cmd import _CONFIRM_ACTIONS
            if not _CONFIRM_ACTIONS:
                t.append("\n  🛡 SECURITY\n", style=f"bold {C['error']}")
                t.append(f"  Confirmations OFF", style=f"bold {C['error']}")

        return Panel(
            t, border_style=C["accent_dark"], box=box.HEAVY,
            title=f"[bold {C['accent_bright']}]◈ QUANTUM CORE ◈[/]",
            title_align="center", padding=(0, 1),
        )


class ThinkingIndicator(Static):
    _frame_idx = reactive(0)
    _active = reactive(False)
    _message = reactive("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._timer: Timer | None = None

    def start(self, message: str = "Processing..."):
        self._active = True
        self._message = message
        if not self._timer:
            self._timer = self.set_interval(0.1, self._tick)
        self.refresh()

    def stop(self):
        self._active = False
        self._message = ""
        if self._timer:
            self._timer.stop()
            self._timer = None
        self.refresh()

    def _tick(self):
        self._frame_idx = (self._frame_idx + 1) % len(SPINNER_FRAMES)
        self.refresh()

    def render(self) -> Text:
        t = Text()
        if self._active:
            spinner = SPINNER_FRAMES[self._frame_idx]
            t.append(f"  {spinner} ", style=f"bold {C['ai_cyan']}")
            t.append(self._message, style=C["text_dim"])
        return t


class StatusBar(Static):
    status_text = reactive("Ready")
    _mode = reactive("chat")
    _model = reactive("")

    MODE_ICONS = {
        "chat": "◆", "agent": "⚡", "debug": "🔧",
        "arch": "🏗", "refactor": "♻", "research": "🔬",
    }
    MODE_COLORS = {
        "chat": C["accent_bright"], "agent": C["pink"], "debug": C["orange"],
        "arch": C["blue"], "refactor": C["success"], "research": C["warning"],
    }

    def render(self) -> Text:
        icon = self.MODE_ICONS.get(self._mode, "◆")
        mcolor = self.MODE_COLORS.get(self._mode, C["accent_bright"])
        model_short = self._model.split("/")[-1][:16] if self._model else ""

        t = Text()
        t.append(f" {icon} {self._mode.upper()}", style=f"bold {mcolor}")
        t.append("  │  ", style=C["accent_dark"])
        if model_short:
            t.append(model_short, style=f"bold {C['text']}")
            t.append("  │  ", style=C["accent_dark"])
        t.append(self.status_text, style=C["ai_cyan"])
        t.append("  │  ", style=C["accent_dark"])
        t.append("Esc Stop  │  Ctrl+Shift+C Copy  │  Ctrl+V Paste", style=C["text_muted"])
        return t


class ChatLog(RichLog):
    """Chat log with selectable text and word wrap."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._copy_mode = False
        self.auto_scroll = True
        self.wrap = True

    def action_copy_selection(self):
        try:
            selection = self.current_selection
            if selection:
                import subprocess
                if __import__('sys').platform == "win32":
                    process = subprocess.Popen(
                        ['clip'], stdin=subprocess.PIPE
                    )
                    process.communicate(selection.encode('utf-16-le'))
                else:
                    process = subprocess.Popen(
                        ['pbcopy'], stdin=subprocess.PIPE
                    )
                    process.communicate(selection.encode())
        except Exception:
            pass


class ConfirmBar(Vertical):
    """Inline confirmation bar with selectable options."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._visible = False

    def compose(self) -> ComposeResult:
        yield RadioSet(
            RadioButton("Yes (Approve)", id="yes"),
            RadioButton("No (Deny)", id="no"),
            RadioButton("Always Allow (session)", id="always"),
            id="confirm-options",
        )
        yield Static("  ↑↓ navigate  •  Enter select", id="confirm-hint")

    def show(self):
        self._visible = True
        self.styles.display = "block"
        rs = self.query_one("#confirm-options", RadioSet)
        try:
            rs._selected = -1
            rs._pressed = -1
        except AttributeError:
            pass
        rs.refresh()
        rs.focus()

    def hide(self):
        self._visible = False
        self.styles.display = "none"


class QuantTUI(App):
    CSS = """
    Screen {
        background: #0f0a19;
    }
    #sidebar-container {
        width: 36;
        min-width: 32;
        height: 100%;
        background: #0d0117;
    }
    #sidebar {
        height: 100%;
    }
    #workspace {
        width: 1fr;
        height: 100%;
        background: #0f0a19;
    }
    #thinking {
        height: 1;
        background: #0f0a19;
        color: #00f5d4;
    }
    #chat-log {
        height: 1fr;
        border: none;
        background: #0f0a19;
        color: #dce8ff;
        scrollbar-size-vertical: 2;
        scrollbar-color: #6e40c9;
        scrollbar-color-hover: #9d4edd;
        scrollbar-color-active: #bf5fff;
        overflow-x: hidden;
    }
    #input-container {
        height: 3;
        background: #0d0117;
        border: solid #6e40c9;
        margin: 0 1 0 1;
    }
    #prompt-label {
        width: 14;
        color: #00f5d4;
        content-align: center middle;
        background: #0d0117;
    }
    #user-input {
        background: #0d0117;
        color: #dce8ff;
        border: none;
        padding: 0 1 0 0;
        width: 1fr;
    }
    #status-bar {
        height: 1;
        background: #1a0a2e;
        color: #6e6a85;
        dock: bottom;
    }
    #confirm-bar {
        height: auto;
        max-height: 6;
        background: #1a0a2e;
        border: solid #ff6400;
        display: none;
        margin: 0 1 0 1;
    }
    #confirm-options {
        background: #1a0a2e;
        border: none;
        height: auto;
        max-height: 5;
    }
    #confirm-options RadioButton {
        background: #1a0a2e;
        color: #dce8ff;
    }
    #confirm-options RadioButton:hover {
        background: #2a1a3e;
    }
    #confirm-options RadioButton.-active {
        background: #ff6400;
        color: #0d0117;
    }
    #confirm-hint {
        height: 1;
        background: #1a0a2e;
        color: #6e6a85;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Exit", show=True),
        Binding("escape", "cancel_task", "Stop", show=True),
        Binding("ctrl+l", "clear_log", "Clear", show=True),
        Binding("tab", "toggle_focus", "Pane", show=True),
        Binding("ctrl+v", "paste_clipboard", "Paste", show=True),
        Binding("ctrl+shift+c", "copy_last", "Copy", show=True),
    ]

    def __init__(self, provider=None, cfg=None, **kwargs):
        super().__init__(**kwargs)
        self.provider = provider
        self.cfg = cfg
        self._on_submit_callback = None
        self._on_ready_callback = None
        self._on_cancel_callback = None
        self._thinking_active = False
        self._mounted = False
        self._current_task: asyncio.Task | None = None
        import time
        self._session_start = time.time()
        self._tool_call_count = 0
        self._backup_count = 0
        self._total_tokens = 0

    def set_on_submit(self, callback):
        self._on_submit_callback = callback

    def set_on_ready(self, callback):
        self._on_ready_callback = callback

    def set_on_cancel(self, callback):
        self._on_cancel_callback = callback

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Sidebar(id="sidebar-container")
            with Vertical(id="workspace"):
                yield ThinkingIndicator(id="thinking")
                yield ChatLog(id="chat-log", highlight=False, markup=True)
                yield ConfirmBar(id="confirm-bar")
                with Horizontal(id="input-container"):
                    yield Static("  ▲ QUANT ➔", id="prompt-label")
                    yield Input(placeholder="Type a message or /help...", id="user-input")
        yield StatusBar(id="status-bar")

    def on_mount(self):
        self._mounted = True
        self.query_one("#user-input", Input).focus()
        self.set_interval(3.0, self._update_system_stats)
        if self._on_ready_callback:
            self._on_ready_callback()

    def _update_system_stats(self):
        if not self._mounted:
            return
        try:
            sidebar = self.query_one("#sidebar-container", Sidebar)
            sidebar.update_system_stats()
        except Exception:
            pass

    def action_clear_log(self):
        self.query_one("#chat-log", ChatLog).clear()

    def action_toggle_focus(self):
        log = self.query_one("#chat-log", ChatLog)
        inp = self.query_one("#user-input", Input)
        if log.has_focus:
            inp.focus()
        else:
            log.focus()

    def action_cancel_task(self):
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None
            self._stop_thinking()
            from quant.ui.i18n import t
            log = self.query_one("#chat-log", ChatLog)
            log.write(f"  [{C['warning']}]{t('interrupted')}[/]")
            if self._on_cancel_callback:
                self._on_cancel_callback()

    def action_paste_clipboard(self):
        try:
            import subprocess
            if __import__('sys').platform == "win32":
                result = subprocess.run(
                    ["powershell", "-command", "Get-Clipboard"],
                    capture_output=True, text=True, timeout=5
                )
                text = result.stdout.strip()
            else:
                result = subprocess.run(
                    ["pbpaste"], capture_output=True, text=True, timeout=5
                )
                text = result.stdout.strip()
            if text:
                inp = self.query_one("#user-input", Input)
                inp.value = text
        except Exception:
            pass

    def action_copy_last(self):
        try:
            log = self.query_one("#chat-log", ChatLog)
            if hasattr(log, '_buffer') and log._buffer:
                last_line = str(log._buffer[-1]) if log._buffer else ""
                if last_line:
                    import subprocess
                    if __import__('sys').platform == "win32":
                        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                        process.communicate(last_line.encode('utf-16-le'))
                    else:
                        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                        process.communicate(last_line.encode())
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed):
        value = event.value
        if value.startswith("/"):
            from quant.ui.help import COMMANDS_LIST
            matches = [c for c in COMMANDS_LIST if c.startswith(value)]
            if matches:
                hint = "  │  ".join(matches[:4])
                self.set_status(hint)
            else:
                self.set_status("Unknown command")
        else:
            self.set_status("Ready")

    def on_input_submitted(self, event: Input.Submitted):
        value = event.value.strip()
        event.input.value = ""
        if not value:
            return

        log = self.query_one("#chat-log", ChatLog)

        if value.startswith("/"):
            self._handle_slash(value, log)
            return

        log.write(Panel(
            Text(value, style=f"bold {C['text']}"),
            border_style=C["accent_dark"], box=box.ROUNDED,
            title=f"[bold {C['accent_dark']}]YOU[/]", title_align="left",
            padding=(0, 1),
        ))

        self._start_thinking("Agent is processing...")
        if self._on_submit_callback:
            self._current_task = asyncio.ensure_future(self._on_submit_callback(value))

    def on_radio_set_changed(self, event: RadioSet.Changed):
        global _CONFIRM_RESULT, _CONFIRM_ALWAYS, _CONFIRM_FUT
        if not _CONFIRM_FUT or _CONFIRM_FUT.done():
            return

        option_id = event.pressed.id

        if option_id == "yes":
            _CONFIRM_RESULT = True
        elif option_id == "no":
            _CONFIRM_RESULT = False
        elif option_id == "always":
            _CONFIRM_ALWAYS = True
            _CONFIRM_RESULT = True

        choice_map = {
            "yes": "confirm_approved",
            "no": "confirm_denied",
            "always": "confirm_always"
        }
        from quant.ui.i18n import t
        log = self.query_one("#chat-log", ChatLog)
        log.write(f"  [{C['text_muted']}]→ {t(choice_map[option_id])}[/]")

        bar = self.query_one("#confirm-bar", ConfirmBar)
        bar.hide()
        self.query_one("#user-input", Input).focus()

        if not _CONFIRM_FUT.done():
            _CONFIRM_FUT.set_result(_CONFIRM_RESULT)

    def _handle_slash(self, cmd: str, log: RichLog):
        parts = cmd.strip().split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if command == "/help":
            from quant.ui.help import get_help_text
            text = get_help_text(arg if arg else "")
            log.write(Panel(text, title=f"[bold {C['accent_bright']}]◆ QUANT HELP[/]",
                            border_style=C["accent_dark"], box=box.ROUNDED))

        elif command == "/clear":
            log.clear()
            log.write(f"  [{C['success']}]History cleared.[/]")

        elif command == "/status":
            info = self.provider.get_info() if self.provider else {}
            t = Table(box=None, show_header=False, padding=(0, 1))
            t.add_column(style=C["text_muted"], width=12)
            t.add_column(style=C["text"])
            t.add_row("provider", f"[bold {C['accent_bright']}]{info.get('provider', '?')}[/]")
            t.add_row("model", f"[bold {C['text']}]{info.get('model', '?')}[/]")
            t.add_row("context", f"[bold {C['accent']}]{info.get('context', 0) // 1024}k[/]")
            log.write(Panel(t, title=f"[bold {C['accent_bright']}]SYSTEM STATUS[/]",
                            border_style=C["accent_dark"], box=box.ROUNDED))

        elif command == "/tokens":
            sidebar = self.query_one("#sidebar-container", Sidebar)
            used = sidebar._ctx_used
            total = sidebar._ctx_total
            pct = min(used / total * 100, 100) if total > 0 else 0
            log.write(f"  [{C['accent']}]Tokens:[/] {used:,} / {total:,} ({pct:.0f}%)")

        elif command == "/mode":
            valid = ["chat", "agent", "debug", "arch", "refactor", "research"]
            if arg in valid:
                self.cfg.mode = arg
                self.query_one("#status-bar", StatusBar)._mode = arg
                log.write(f"  [{C['success']}]Mode → {arg.upper()}[/]")
            else:
                log.write(f"  [{C['error']}]Choose: {', '.join(valid)}[/]")

        elif command == "/confirm":
            if arg == "off":
                self.cfg.confirm_actions = False
                set_session_allow(False)
                from quant.tools.cmd import set_confirm as set_cmd_confirm
                from quant.tools.write_file import set_confirm as set_write_confirm
                from quant.tools.edit_file import set_edit_confirm as set_edit_confirm
                set_cmd_confirm(False)
                set_write_confirm(False)
                set_edit_confirm(False)
                self.cfg.save()
                log.write(f"  [{C['success']}]Confirmations disabled.[/]")
            elif arg == "on":
                self.cfg.confirm_actions = True
                set_session_allow(False)
                from quant.tools.cmd import set_confirm as set_cmd_confirm
                from quant.tools.write_file import set_confirm as set_write_confirm
                from quant.tools.edit_file import set_confirm as set_edit_confirm
                set_cmd_confirm(True)
                set_write_confirm(True)
                set_edit_confirm(True)
                self.cfg.save()
                log.write(f"  [{C['success']}]Confirmations enabled.[/]")
            elif arg == "allow":
                set_session_allow(True)
                log.write(f"  [{C['warning']}]Session: all actions auto-approved until restart.[/]")
            else:
                state = "ON" if self.cfg.confirm_actions else "OFF"
                allow = " (Allow All active)" if _CONFIRM_ALWAYS else ""
                log.write(f"  [{C['text']}]Confirmations: {state}{allow}. Use /confirm on|off|allow[/]")

        elif command == "/restore":
            if not arg:
                log.write(f"  [{C['text']}]Usage: /restore <file_path>[/]")
            else:
                from pathlib import Path
                from quant.tools.safety import restore_latest_backup
                from quant.tools.filesystem import _resolve, get_working_dir
                p = _resolve(arg, get_working_dir())
                ok, msg = restore_latest_backup(p)
                if ok:
                    log.write(f"  [{C['success']}]{msg}[/]")
                else:
                    log.write(f"  [{C['error']}]{msg}[/]")

        elif command == "/export":
            from pathlib import Path
            from quant.ui.i18n import t
            filename = arg or "conversation.md"
            lines = [f"# QUANT Conversation\n"]
            for m in self._get_session_messages():
                role = m.get("role", "?").upper()
                content = m.get("content", "")
                lines.append(f"## {role}\n{content}\n")
            try:
                Path(filename).write_text("\n".join(lines), encoding="utf-8")
                log.write(f"  [{C['success']}]{t('export_done', file=filename)}[/]")
            except Exception as e:
                log.write(f"  [{C['error']}]{t('export_error', error=str(e))}[/]")

        elif command == "/theme":
            from quant.ui.i18n import t
            valid = ["dark", "purple", "neon"]
            if arg in valid:
                self._apply_theme(arg)
                log.write(f"  [{C['success']}]{t('theme_changed', name=arg)}[/]")
            else:
                log.write(f"  [{C['text']}]Choose: {', '.join(valid)}[/]")

        elif command == "/lang":
            from quant.ui.i18n import set_lang, get_lang, list_langs, t
            valid = list_langs()
            if arg in valid:
                set_lang(arg)
                log.write(f"  [{C['success']}]{t('lang_changed', name=arg)}[/]")
            else:
                log.write(f"  [{C['text']}]Choose: {', '.join(valid)} (current: {get_lang()})[/]")

        elif command == "/exit":
            self._show_session_summary()
            self.exit()

        else:
            log.write(f"  [{C['error']}]Unknown: {command}. Type /help[/]")

    def _start_thinking(self, message: str = ""):
        if not self._mounted:
            return
        self._thinking_active = True
        self.query_one("#thinking", ThinkingIndicator).start(message or "Processing...")
        self.query_one("#status-bar", StatusBar).status_text = "Thinking..."

    def _stop_thinking(self):
        if not self._mounted:
            return
        self._thinking_active = False
        try:
            self.query_one("#thinking", ThinkingIndicator).stop()
            self.query_one("#status-bar", StatusBar).status_text = "Ready"
        except Exception:
            pass

    def _show_confirm_prompt(self, tool_name: str, display: str):
        if not self._mounted:
            return
        log = self.query_one("#chat-log", ChatLog)
        log.write(Panel(
            f"[bold {C['warning']}]⚠ {tool_name}[/]  [{C['text_muted']}]{display}[/]",
            border_style=C["warning"],
            box=box.ROUNDED,
            title=f"[bold {C['warning']}]CONFIRM ACTION[/]",
            title_align="left",
            padding=(0, 1),
        ))
        bar = self.query_one("#confirm-bar", ConfirmBar)
        bar.show()
        self.set_status("Waiting for confirmation...")

    def _hide_confirm_prompt(self):
        if not self._mounted:
            return
        bar = self.query_one("#confirm-bar", ConfirmBar)
        bar.hide()
        self.set_status("Ready")

    def add_assistant_message(self, message: str, model: str = ""):
        if not self._mounted:
            return
        self._stop_thinking()
        log = self.query_one("#chat-log", ChatLog)
        label = model.split("/")[-1] if model else "QUANT"
        try:
            from rich.markdown import Markdown
            md = Markdown(message)
            log.write(Panel(md, border_style=C["accent"], box=box.ROUNDED,
                            title=f"[bold {C['ai_cyan']}]✦ {label}[/]",
                            title_align="left", padding=(0, 1)))
        except Exception:
            log.write(Panel(message, border_style=C["accent"], box=box.ROUNDED,
                            title=f"[bold {C['ai_cyan']}]✦ {label}[/]",
                            title_align="left", padding=(0, 1)))

    def start_stream(self, model: str = ""):
        if not self._mounted:
            return
        self._stop_thinking()
        self._stream_buffer = ""
        self._stream_label = model.split("/")[-1] if model else "QUANT"
        self.set_status("Streaming...")

    def append_stream(self, token: str):
        if not self._mounted:
            return
        self._stream_buffer += token

    def finish_stream(self):
        if not self._mounted:
            return
        if hasattr(self, '_stream_buffer') and self._stream_buffer:
            self.add_assistant_message(self._stream_buffer, self._stream_label)
            self._stream_buffer = ""
        self.set_status("Ready")

    def _get_session_messages(self) -> list[dict]:
        if hasattr(self, '_session'):
            return self._session.to_api_format()
        return []

    def _apply_theme(self, theme: str):
        from quant.ui.themes import set_theme, get_theme
        set_theme(theme)
        t = get_theme(theme)
        try:
            self.query_one("#sidebar-container").styles.background = t["panel"]
            self.query_one("#workspace").styles.background = t["bg"]
            self.query_one("#input-container").styles.background = t["panel"]
            self.query_one("#status-bar").styles.background = t["status_bg"]
        except Exception:
            pass

    def _show_session_summary(self):
        import time
        from quant.ui.renderer import print_session_summary
        from quant.ui.i18n import t
        elapsed = time.time() - self._session_start
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        duration = f"{mins} min {secs} sec" if mins > 0 else f"{secs} sec"
        print_session_summary(
            duration=duration,
            tool_calls=self._tool_call_count,
            backups=self._backup_count,
            tokens=self._total_tokens,
            status=t("summary_completed"),
        )

    def add_tool_message(self, tool_name: str, args: dict, success: bool, preview: str = ""):
        if not self._mounted:
            return
        self._tool_call_count += 1
        if "backup" in preview.lower():
            self._backup_count += 1
        log = self.query_one("#chat-log", ChatLog)
        icon = f"[{C['success']}]" + "✓" + "[/]" if success else f"[{C['error']}]" + "✗" + "[/]"
        args_short = " ".join(f"{k}={str(v)[:30]}" for k, v in list(args.items())[:3])
        log.write(f"  [{C['pink']}]⚙ {tool_name}[/] {icon}  [{C['text_muted']}]{args_short}[/]")
        if preview:
            log.write(f"    [{C['text_muted']}]{preview[:120]}[/]")

    def add_thinking(self, text: str):
        if not self._mounted:
            return
        log = self.query_one("#chat-log", ChatLog)
        log.write(f"  [{C['ai_cyan']}]● THOUGHTS[/] [{C['text_muted']}]{text}[/]")

    def update_system(self, **kwargs):
        if not self._mounted:
            return
        if "ctx_used" in kwargs:
            self._total_tokens = kwargs["ctx_used"]
        sidebar = self.query_one("#sidebar-container", Sidebar)
        sidebar.update_info(**kwargs)
        if "model" in kwargs:
            self.query_one("#status-bar", StatusBar)._model = kwargs["model"]
        if "mode" in kwargs:
            self.query_one("#status-bar", StatusBar)._mode = kwargs["mode"]

    def set_status(self, text: str):
        if not self._mounted:
            return
        self.query_one("#status-bar", StatusBar).status_text = text

    def add_system_message(self, text: str, style: str = ""):
        if not self._mounted:
            return
        self._stop_thinking()
        log = self.query_one("#chat-log", ChatLog)
        s = style or C["text_muted"]
        log.write(f"  [{s}]✦ {text}[/]")

    def add_error_message(self, text: str):
        if not self._mounted:
            return
        self._stop_thinking()
        log = self.query_one("#chat-log", ChatLog)
        log.write(Panel(
            f"[{C['error']}]{text}[/]", border_style=C["error"],
            title=f"[{C['error']}]ERROR[/]", title_align="left",
            box=box.ROUNDED, padding=(0, 1),
        ))


_tui_app_ref: QuantTUI | None = None


def _get_tui_app() -> QuantTUI | None:
    return _tui_app_ref


def _set_tui_app(app: QuantTUI):
    global _tui_app_ref
    _tui_app_ref = app
