"""QUANT CLI — WRITE_FILE с подтверждением."""
from __future__ import annotations
from pathlib import Path
from quant.tools.base import BaseTool, ToolResult
from quant.tools.filesystem import get_working_dir

_CONFIRM_ACTIONS: bool = True

def set_confirm(value: bool) -> None:
    global _CONFIRM_ACTIONS
    _CONFIRM_ACTIONS = value

def get_confirm() -> bool:
    return _CONFIRM_ACTIONS


class WriteFileTool(BaseTool):
    name = "WRITE_FILE"
    description = (
        "Write or create any file on the user's machine. "
        "Can create .txt, .py, .js, .html, .json, .md, .csv — any format. "
        "Relative paths are resolved from the working directory. "
        "Set overwrite=true to replace existing files."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path. Use forward slashes. Relative = from working dir."
            },
            "content": {
                "type": "string",
                "description": "Text content to write into the file."
            },
            "overwrite": {
                "type": "boolean",
                "description": "Overwrite if file already exists (default: true)."
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)."
            },
        },
        "required": ["path", "content"],
    }

    async def execute(
        self,
        path: str,
        content: str,
        overwrite: bool = True,
        encoding: str = "utf-8",
        **kwargs,
    ) -> ToolResult:
        from quant.tools.filesystem import _resolve
        from quant.tools.safety import is_path_blocked
        cwd = get_working_dir()
        p   = _resolve(path, cwd)

        blocked, reason = is_path_blocked(str(p))
        if blocked:
            return ToolResult(False, {}, error=f"BLOCKED: {reason}")

        if p.exists() and not overwrite:
            return ToolResult(False, {}, error=f"File exists: {p}. Set overwrite=true to replace.")

        if _CONFIRM_ACTIONS:
            from quant.ui.tui import _get_tui_app, session_allow_all
            if not session_allow_all():
                app = _get_tui_app()
                if app:
                    from quant.ui.tui import tui_confirm
                    if not await tui_confirm("WRITE_FILE", {"path": str(p), "lines": content.count(chr(10)) + 1}):
                        return ToolResult(False, {}, error="Cancelled by user.")
                else:
                    from quant.ui.renderer import print_confirm_prompt
                    if not print_confirm_prompt("WRITE_FILE", {"path": str(p), "lines": content.count(chr(10)) + 1}):
                        return ToolResult(False, {}, error="Cancelled by user.")

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            existed = p.exists()
            if existed:
                from quant.tools.safety import create_backup
                create_backup(p)
            p.write_text(content, encoding=encoding)
            return ToolResult(True, {
                "path":    str(p),
                "bytes":   len(content.encode(encoding)),
                "lines":   content.count("\n") + 1,
                "created": not existed,
            })
        except Exception as e:
            return ToolResult(False, {}, error=str(e))
