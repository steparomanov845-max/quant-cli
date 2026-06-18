"""QUANT CLI — REPL."""
from __future__ import annotations
import asyncio
import sys
import os
from pathlib import Path

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    # Enable VT processing for ANSI escape codes
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console

from quant.agent.agent import QuantAgent
from quant.core.config import QuantConfig, CONFIG_DIR
from quant.core.context import ContextEngine
from quant.core.session import Session
from quant.providers import get_provider
from quant.tools import get_tools
from quant.tools.filesystem import set_working_dir, get_working_dir
from quant.tools.write_file import set_confirm as set_write_confirm
from quant.tools.edit_file import set_confirm as set_edit_confirm
from quant.tools.cmd import set_confirm as set_cmd_confirm
from quant.ui import renderer
from quant.ui.i18n import load_lang_from_config

load_lang_from_config()

console = Console()

PT_STYLE = Style.from_dict({
    "prompt":         "#bf5fff bold",
    "bottom-toolbar": "bg:#0d0117 #6e6a85",
})

SLASH_COMMANDS = {
    "/mode <name>":    "chat | agent | debug | arch | refactor | research",
    "/model [auto]":   "List models / auto-detect / switch (v0 API with state info)",
    "/cd <path>":      "Change working directory",
    "/pwd":            "Show current working directory",
    "/confirm on|off": "Toggle action confirmation dialogs",
    "/lang <name>":    "Switch language: en | ru",
    "/tokens":         "Show token usage for current session",
    "/history":        "Show conversation history summary",
    "/save <file>":    "Save conversation to markdown file",
    "/compact":        "Compact conversation history (keep last 20 messages)",
    "/status":         "RAM, CPU, provider info",
    "/clear":          "Clear conversation history",
    "/help":           "Show this help",
    "/exit":           "Exit QUANT",
}

_ctx_state = {"used": 0, "total": 32768, "model": "model", "mode": "chat"}


def _bottom_toolbar():
    used  = _ctx_state["used"]
    total = _ctx_state["total"]
    model = _ctx_state["model"].split("/")[-1][:20]
    mode  = _ctx_state["mode"]
    cwd   = str(get_working_dir())[-35:]

    icons  = {"chat":"◆","agent":"⚡","debug":"🐛","arch":"🏗","refactor":"♻","research":"🔬"}
    mcolors = {
        "chat":"#bd93f9","agent":"#ff79c6","debug":"#ffb86c",
        "arch":"#8be9fd","refactor":"#50fa7b","research":"#f1fa8c",
    }
    icon   = icons.get(mode, "◆")
    mcolor = mcolors.get(mode, "#bd93f9")

    if total > 0 and used > 0:
        pct    = min(used / total * 100, 100)
        color  = "#50fa7b" if pct < 60 else "#f1fa8c" if pct < 85 else "#ff5555"
        filled = int(14 * pct / 100)
        bar    = "█" * filled + "░" * (14 - filled)
        ctx_part = f'<style fg="{color}">{bar} {used:,}/{total:,} ({pct:.0f}%)</style>'
    else:
        ctx_part = f'<style fg="#6e6a85">{total//1024}k ctx</style>'

    return HTML(
        f' <style fg="{mcolor}"><b>{icon} {mode.upper()}</b></style>'
        f'  <style fg="#6e40c9">│</style>'
        f'  <style fg="white"><b>{model}</b></style>'
        f'  <style fg="#6e40c9">│</style>'
        f'  {ctx_part}'
        f'  <style fg="#6e40c9">│</style>'
        f'  <style fg="#6e6a85">{cwd}</style>'
    )


async def _run_agent(cfg, provider, session: Session, context: ContextEngine, task: str) -> None:
    tools  = get_tools()
    system = context.build_system_context(cfg.mode, provider.get_info())

    full_response = []
    def on_token(token: str):
        full_response.append(token)
        print(token, end="", flush=True)

    agent  = QuantAgent(
        provider=provider,
        tools=tools,
        mode=cfg.mode,
        model_name=cfg.model,
        on_token=on_token,
    )
    print()
    result = await agent.run(task, history=session.to_api_format(), system=system)
    print()

    session.add("user", task)
    session.add("assistant", result)

    usage = getattr(provider, "last_usage", {})
    used  = usage.get("total_tokens", 0)
    if used:
        _ctx_state["used"] = used


async def _handle_slash(cmd: str, cfg: QuantConfig, provider, session: Session):
    parts   = cmd.strip().split(maxsplit=1)
    command = parts[0].lower()
    arg     = parts[1].strip() if len(parts) > 1 else ""

    if command == "/help":
        renderer.print_help(SLASH_COMMANDS)

    elif command == "/status":
        from quant.ui.status_bar import print_status
        print_status(provider.get_info(), cfg.mode)

    elif command == "/clear":
        session.clear()
        _ctx_state["used"] = 0
        renderer.print_success("History cleared.")

    elif command == "/pwd":
        cwd = get_working_dir()
        renderer.print_info(f"Working directory: [bold white]{cwd}[/]")

    elif command == "/cd":
        if arg:
            new_path = Path(arg.replace("\\", "/"))
            if not new_path.is_absolute():
                new_path = get_working_dir() / new_path
            if new_path.exists() and new_path.is_dir():
                set_working_dir(new_path)
                renderer.print_success(f"Working dir -> {new_path}")
            else:
                renderer.print_error(f"Directory not found: {new_path}")
        else:
            renderer.print_info(f"Current: {get_working_dir()}")

    elif command == "/confirm":
        if arg == "off":
            set_write_confirm(False)
            set_edit_confirm(False)
            set_cmd_confirm(False)
            cfg.confirm_actions = False
            cfg.save()
            renderer.print_success("Confirmations disabled.")
        elif arg == "on":
            set_write_confirm(True)
            set_edit_confirm(True)
            set_cmd_confirm(True)
            cfg.confirm_actions = True
            cfg.save()
            renderer.print_success("Confirmations enabled.")
        else:
            state = "ON" if cfg.confirm_actions else "OFF"
            renderer.print_info(f"Confirmations: {state}. Use /confirm on|off")

    elif command == "/tokens":
        used  = _ctx_state["used"]
        total = _ctx_state["total"]
        pct   = min(used / total * 100, 100) if total > 0 else 0
        msgs  = len(session.messages)
        renderer.print_info(f"[bold #bd93f9]Token Usage[/]")
        renderer.print_info(f"  Used:      [white]{used:,}[/] / [white]{total:,}[/] ({pct:.0f}%)")
        renderer.print_info(f"  Remaining: [white]{total - used:,}[/]")
        renderer.print_info(f"  Messages:  [white]{msgs}[/]")
        renderer.print_info(f"  Model:     [white]{cfg.model}[/]")

    elif command == "/history":
        msgs = session.messages
        if not msgs:
            renderer.print_info("No messages yet.")
        else:
            renderer.print_info(f"[bold #bd93f9]History[/] ([white]{len(msgs)}[/] messages)")
            for i, m in enumerate(msgs[-10:], max(1, len(msgs) - 9)):
                role_color = "#50fa7b" if m.role == "user" else "#bd93f9"
                preview = m.content[:60].replace("\n", " ")
                if len(m.content) > 60:
                    preview += "..."
                renderer.print_info(f"  [{role_color}]{m.role}[/]  {preview}")

    elif command == "/save":
        if not arg:
            arg = "conversation.md"
        try:
            lines = ["# QUANT Conversation\n"]
            for m in session.messages:
                role = m.role.upper()
                lines.append(f"## {role}\n{m.content}\n")
            Path(arg).write_text("\n".join(lines), encoding="utf-8")
            renderer.print_success(f"Saved to [bold white]{arg}[/]")
        except Exception as e:
            renderer.print_error(str(e))

    elif command == "/compact":
        before = len(session.messages)
        if before > 20:
            session.messages = session.messages[-20:]
            after = len(session.messages)
            renderer.print_success(f"Compacted: {before} -> {after} messages")
        else:
            renderer.print_info(f"Only {before} messages, no compaction needed.")

    elif command == "/mode":
        valid = ["chat", "agent", "debug", "arch", "refactor", "research"]
        if arg in valid:
            cfg.mode = arg
            _ctx_state["mode"] = arg
            cfg.save()
            renderer.print_mode_change(arg)
        else:
            renderer.print_error(f"Choose: {', '.join(valid)}")

    elif command == "/model":
        if arg == "auto" or arg == "detect":
            health = await provider.health_check()
            if health.get("status") == "ok":
                cfg.model = provider.model
                _ctx_state["model"] = provider.model
                _ctx_state["total"] = provider.context_size
                _ctx_state["used"]  = 0
                cfg.save()
                renderer.print_success(
                    f"Auto-detected: [bold #bd93f9]{provider.model}[/] "
                    f"ctx: [bold #bd93f9]{provider.context_size // 1024}k[/]"
                )
            else:
                renderer.print_error(health.get("message", "Health check failed"))
        elif arg:
            cfg.model = arg
            provider.model = arg
            _ctx_state["model"] = arg
            cfg.save()
            renderer.print_success(f"Model -> {arg}")
            health = await provider.health_check()
            if health.get("status") == "ok":
                _ctx_state["total"] = provider.context_size
                _ctx_state["used"]  = 0
                renderer.print_success(f"Context: [bold #bd93f9]{provider.context_size // 1024}k[/]")
            else:
                renderer.print_error(health.get("message", "Health check failed"))
        else:
            v0_models = []
            if hasattr(provider, "list_models_v0"):
                v0_models = await provider.list_models_v0()

            if not v0_models:
                models = await provider.list_models()
                if not models:
                    renderer.print_info("No models found.")
                else:
                    for i, m in enumerate(models, 1):
                        marker = " <- current" if m == cfg.model else ""
                        renderer.print_info(f"  {i}. {m}{marker}")
            else:
                from rich.table import Table as RichTable
                from rich import box as rbox
                t = RichTable(box=rbox.SIMPLE, show_header=True, padding=(0, 1),
                              title="[bold #bf5fff]LM Studio Models[/]")
                t.add_column("#", style="#6e6a85", width=3)
                t.add_column("Model", style="bold white")
                t.add_column("State", justify="center")
                t.add_column("Context", justify="right", style="#bd93f9")
                t.add_column("Capabilities", style="#6e6a85")

                for i, m in enumerate(v0_models, 1):
                    mid   = m["id"]
                    state = m.get("state", "?")
                    ctx   = m.get("max_context_length", 0)
                    lctx  = m.get("loaded_context_length")
                    caps  = ", ".join(m.get("capabilities", []))

                    if state == "loaded":
                        state_str = "[bold #50fa7b]● loaded[/]"
                        ctx_str = f"[bold #50fa7b]{(lctx or ctx) // 1024}k[/]"
                    else:
                        state_str = "[#6e6a85]○ idle[/]"
                        ctx_str = f"[#6e6a85]{ctx // 1024}k[/]"

                    marker = " <" if mid == cfg.model else ""
                    t.add_row(str(i), f"{mid}{marker}", state_str, ctx_str, caps)

                console.print()
                console.print(t)
                console.print()

                renderer.print_info("[bold #bd93f9]Options:[/]")
                renderer.print_info("  [bold #ff79c6]auto[/]  - auto-detect loaded model")
                renderer.print_info("  [bold #ff79c6]N[/]     - select by number")
                renderer.print_info("  [bold #ff79c6]name[/]  - set model name directly")

                try:
                    choice = console.input(
                        "\n  [bold #6e40c9]Select[/] [dim](auto/N/name)[/] [bold #6e40c9]>[/] "
                    ).strip()

                    if choice.lower() == "auto":
                        health = await provider.health_check()
                        if health.get("status") == "ok":
                            cfg.model = provider.model
                            _ctx_state["model"] = provider.model
                            _ctx_state["total"] = provider.context_size
                            _ctx_state["used"]  = 0
                            cfg.save()
                            renderer.print_success(
                                f"Auto-detected: [bold #bd93f9]{provider.model}[/] "
                                f"ctx: [bold #bd93f9]{provider.context_size // 1024}k[/]"
                            )
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(v0_models):
                            selected = v0_models[idx]
                            cfg.model = selected["id"]
                            provider.model = selected["id"]
                            _ctx_state["model"] = selected["id"]
                            ctx_val = selected.get("max_context_length", 32768)
                            cfg.context_size = ctx_val
                            provider.context_size = ctx_val
                            _ctx_state["total"] = ctx_val
                            _ctx_state["used"]  = 0
                            cfg.save()
                            renderer.print_success(
                                f"Model: [bold #bd93f9]{selected['id']}[/] "
                                f"ctx: [bold #bd93f9]{ctx_val // 1024}k[/]"
                            )
                        else:
                            renderer.print_error("Invalid number")
                    elif choice:
                        cfg.model = choice
                        provider.model = choice
                        _ctx_state["model"] = choice
                        cfg.save()
                        renderer.print_success(f"Model -> {choice}")
                except (KeyboardInterrupt, EOFError):
                    renderer.print_info("Cancelled.")

    elif command == "/lang":
        from quant.ui.i18n import set_lang, get_lang, list_langs, t
        valid = list_langs()
        if arg in valid:
            set_lang(arg)
            cfg.lang = arg
            cfg.save()
            renderer.print_success(t('lang_changed', name=arg))
        else:
            renderer.print_info(f"Choose: {', '.join(valid)} (current: {get_lang()})")

    elif command == "/exit":
        raise SystemExit(0)

    else:
        renderer.print_error(f"Unknown command: {command}. Type /help for list.")

    return cfg, provider


async def repl(cfg: QuantConfig) -> None:
    launch_dir = Path.cwd()
    set_working_dir(launch_dir)
    set_write_confirm(cfg.confirm_actions)
    set_edit_confirm(cfg.confirm_actions)
    set_cmd_confirm(cfg.confirm_actions)

    renderer.print_banner()

    provider = get_provider(cfg)
    health   = await provider.health_check()

    if health.get("status") != "ok":
        renderer.print_error(health.get("message", "Provider error"))
        renderer.print_info("Make sure LM Studio is running on port 1234.")
    else:
        updated = False

        if getattr(provider, "_model_detected", False):
            if provider.model != cfg.model:
                cfg.model = provider.model
                updated = True

        if getattr(provider, "_context_detected", False):
            if provider.context_size != cfg.context_size:
                cfg.context_size = provider.context_size
                updated = True

        if updated:
            cfg.save()

        _ctx_state["total"] = provider.context_size
        _ctx_state["model"] = cfg.model
        _ctx_state["mode"]  = cfg.mode

        renderer.splash_animation(model=cfg.model, ctx=provider.context_size)

        if getattr(provider, "_model_detected", False):
            renderer.print_success(
                f"Model: [bold #bd93f9]{provider.model}[/] [dim](auto-detected)[/]"
            )
        else:
            renderer.print_info(f"Model: [bold white]{provider.model}[/]")

        if getattr(provider, "_context_detected", False):
            renderer.print_success(
                f"Context: [bold #bd93f9]{provider.context_size // 1024}k[/] [dim](auto-detected)[/]"
            )

        renderer.print_success(f"Connected  |  [bold white]{launch_dir}[/]")

    session = Session()
    context = ContextEngine(project_root=launch_dir, max_context_chars=cfg.max_context_chars)

    history_file = CONFIG_DIR / "history"
    CONFIG_DIR.mkdir(exist_ok=True)
    try:
        pt_history = FileHistory(str(history_file))
    except Exception:
        pt_history = InMemoryHistory()

    pt = PromptSession(
        history=pt_history,
        style=PT_STYLE,
        bottom_toolbar=_bottom_toolbar,
        refresh_interval=1.0,
    )

    renderer.print_info("\n  /help for commands  |  Ctrl+C to exit\n")

    while True:
        try:
            user_input = await pt.prompt_async("")
        except (KeyboardInterrupt, EOFError):
            renderer.print_info("\n  Goodbye.\n")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            result = await _handle_slash(user_input, cfg, provider, session)
            if result:
                cfg, provider = result
            _ctx_state["mode"]  = cfg.mode
            _ctx_state["model"] = cfg.model
            continue

        renderer.print_user(user_input)

        pruned = session.prune()
        if pruned:
            renderer.print_info(f"Context pruned: {pruned} old messages removed")

        try:
            await _run_agent(cfg, provider, session, context, user_input)
        except Exception as e:
            renderer.print_error(str(e))

    if hasattr(provider, "close"):
        try:
            await provider.close()
        except Exception:
            pass
