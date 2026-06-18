"""QUANT CLI — EDIT_FILE с подтверждением."""
from __future__ import annotations
from pathlib import Path
from quant.tools.base import BaseTool, ToolResult
from quant.tools.filesystem import get_working_dir

_CONFIRM_ACTIONS: bool = True

def set_confirm(value: bool) -> None:
    global _CONFIRM_ACTIONS
    _CONFIRM_ACTIONS = value


class EditFileTool(BaseTool):
    name = "EDIT_FILE"
    description = "Edit file by replacing exact string. Always read the file first."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path."},
            "old_str": {"type": "string", "description": "Exact text to find and replace."},
            "new_str": {"type": "string", "description": "New text to insert."},
        },
        "required": ["path", "old_str", "new_str"],
    }

    async def execute(self, path: str, old_str: str, new_str: str, **kwargs):
        from quant.tools.filesystem import _resolve, _fix_path
        from quant.tools.safety import is_path_blocked
        cwd = get_working_dir()
        p   = _resolve(path, cwd)

        blocked, reason = is_path_blocked(str(p))
        if blocked:
            return ToolResult(False, {}, error=f"BLOCKED: {reason}")

        if not p.exists():
            return ToolResult(False, {}, error=f"File not found: {p}")

        original = p.read_text(encoding="utf-8")
        if old_str not in original:
            return ToolResult(False, {}, error="old_str not found in file")

        if _CONFIRM_ACTIONS:
            from quant.ui.tui import _get_tui_app, session_allow_all
            if not session_allow_all():
                app = _get_tui_app()
                if app:
                    from quant.ui.tui import tui_confirm
                    if not await tui_confirm("EDIT_FILE", {"path": str(p), "old": old_str[:80], "new": new_str[:80]}):
                        return ToolResult(False, {}, error="Cancelled by user.")
                else:
                    from quant.ui.renderer import print_confirm_prompt
                    if not print_confirm_prompt("EDIT_FILE", {"path": str(p), "old": old_str[:80], "new": new_str[:80]}):
                        return ToolResult(False, {}, error="Cancelled by user.")

        updated = original.replace(old_str, new_str, 1)
        from quant.tools.safety import create_backup
        create_backup(p)
        p.write_text(updated, encoding="utf-8")
        return ToolResult(True, {"path": str(p), "changed": True})
