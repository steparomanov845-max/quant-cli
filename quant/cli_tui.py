"""QUANT CLI — TUI mode (full-screen Textual interface)."""
from __future__ import annotations
import asyncio
import sys
import os
from pathlib import Path

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from quant.core.config import QuantConfig, CONFIG_DIR
from quant.core.session import Session
from quant.core.context import ContextEngine
from quant.providers import get_provider
from quant.tools import get_tools
from quant.tools.filesystem import set_working_dir, get_working_dir
from quant.tools.write_file import set_confirm as set_write_confirm
from quant.tools.edit_file import set_confirm as set_edit_confirm
from quant.tools.cmd import set_confirm as set_cmd_confirm
from quant.ui.tui import QuantTUI, _set_tui_app
from quant.ui.i18n import load_lang_from_config
from quant.agent.agent import QuantAgent

load_lang_from_config()


class QuantApp:
    def __init__(self, cfg: QuantConfig):
        self.cfg = cfg
        self.provider = get_provider(cfg)
        self.session = Session()
        self.launch_dir = Path.cwd()
        self.context = ContextEngine(project_root=self.launch_dir, max_context_chars=cfg.max_context_chars)
        self.tui = QuantTUI(provider=self.provider, cfg=cfg)
        self.tui._session = self.session
        self.tui.set_on_submit(self._on_user_input)
        self.tui.set_on_ready(self._on_ready)
        self.tui.set_on_cancel(self._on_cancel)

        _set_tui_app(self.tui)

        set_working_dir(self.launch_dir)
        set_write_confirm(cfg.confirm_actions)
        set_edit_confirm(cfg.confirm_actions)
        set_cmd_confirm(cfg.confirm_actions)

    def _on_ready(self):
        asyncio.ensure_future(self._init_provider())

    def _on_cancel(self):
        self.tui.set_status("Cancelled")

    async def _init_provider(self):
        health = await self.provider.health_check()

        if health.get("status") == "ok":
            self.cfg.model = self.provider.model
            self.tui.update_system(
                model=self.cfg.model,
                provider=self.cfg.provider,
                host=self.provider.BASE,
                dir=str(self.launch_dir),
                files=0,
                ctx_used=0,
                ctx_total=self.provider.context_size,
                mode=self.cfg.mode,
            )
            self.tui.add_system_message(
                f"Connected: {self.cfg.model} | {self.provider.context_size // 1024}k ctx",
                style="#50fa7b",
            )
        else:
            self.tui.add_error_message(
                f"Connection failed: {health.get('message', 'Unknown error')}"
            )

        self.tui.set_status("Ready")

    async def _on_user_input(self, text: str):
        if text.startswith("/"):
            return

        self.tui.set_status("Thinking...")

        try:
            self.session.token_limit = int(self.provider.context_size * 0.85)
            pruned = self.session.prune()
            if pruned:
                self.tui.add_system_message(f"Context pruned: removed {pruned} old messages")

            tools = get_tools()
            system = self.context.build_system_context(
                self.cfg.mode, self.provider.get_info()
            )

            agent = QuantAgent(
                provider=self.provider,
                tools=tools,
                mode=self.cfg.mode,
                model_name=self.cfg.model,
                on_tool=self._on_tool,
                on_token=self._on_token,
            )

            self.tui.start_stream(model=self.cfg.model)
            result = await agent.run(
                text,
                history=self.session.to_api_format(),
                system=system,
            )
            self.tui.finish_stream()

            self.session.add("user", text)
            self.session.add("assistant", result)

            usage = getattr(self.provider, "last_usage", {})
            used = usage.get("total_tokens", 0)
            if used:
                self.tui.update_system(
                    model=self.cfg.model,
                    provider=self.cfg.provider,
                    host=self.provider.BASE,
                    dir=str(self.launch_dir),
                    files=0,
                    ctx_used=used,
                    ctx_total=self.provider.context_size,
                    mode=self.cfg.mode,
                )

        except asyncio.CancelledError:
            self.tui.finish_stream()
        except Exception as e:
            self.tui.add_error_message(str(e))
        finally:
            self.tui._stop_thinking()
            self.tui._current_task = None
            self.tui.set_status("Ready")

    def _on_token(self, token: str):
        self.tui.append_stream(token)

    def _on_tool(self, tool_name: str, args: dict, result):
        self.tui.add_tool_message(
            tool_name, args, result.success,
            preview=str(result)[:120] if result else "",
        )

    async def run(self):
        try:
            await self.tui.run_async()
        finally:
            if hasattr(self.provider, "close"):
                try:
                    await self.provider.close()
                except Exception:
                    pass


def run_tui(cfg: QuantConfig):
    app = QuantApp(cfg)
    asyncio.run(app.run())
