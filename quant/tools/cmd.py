"""QUANT CLI — CMD: shell + python с подтверждением."""
from __future__ import annotations
import contextlib
import io
import re
import shlex
import subprocess
import sys
import traceback
from pathlib import Path
from quant.tools.base import BaseTool, ToolResult
from quant.tools.filesystem import get_working_dir

_CONFIRM_ACTIONS: bool = True

def set_confirm(value: bool) -> None:
    global _CONFIRM_ACTIONS
    _CONFIRM_ACTIONS = value

BLOCKED = [
    r"rm\s+-rf\s+/(?!\w)",
    r"rm\s+-rf\s+~",
    r"format\s+[a-zA-Z]:",
    r"diskpart",
    r":\(\)\s*\{.*\}",
    r"dd\s+if=.*of=/dev/[sh]d",
    r"mkfs\.",
]


class CmdTool(BaseTool):
    name = "CMD"
    description = (
        "Execute shell commands or Python code on the user's machine. "
        "type='shell': runs terminal commands (mkdir, pip install, python script.py, npm, git...). "
        "type='python': executes Python code inline and returns stdout output. "
        "Default cwd is the working directory where quant was launched."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command or Python code to execute."
            },
            "type": {
                "type": "string",
                "enum": ["shell", "python"],
                "description": "shell = terminal command, python = Python code (default: shell)"
            },
            "cwd": {
                "type": "string",
                "description": "Working directory (default: quant launch directory)"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout seconds (default: 60)"
            },
        },
        "required": ["command"],
    }

    async def execute(
        self,
        command: str,
        type: str = "shell",
        cwd: str = "",
        timeout: int = 60,
        **kwargs,
    ) -> ToolResult:
        from quant.tools.safety import is_cmd_blocked
        blocked, reason = is_cmd_blocked(command)
        if blocked:
            return ToolResult(False, {}, error=f"BLOCKED: {reason}")

        if _CONFIRM_ACTIONS:
            from quant.ui.tui import _get_tui_app, session_allow_all
            if not session_allow_all():
                app = _get_tui_app()
                if app:
                    from quant.ui.tui import tui_confirm
                    if not await tui_confirm("CMD", {"command": command, "type": type}):
                        return ToolResult(False, {}, error="Cancelled by user.")
                else:
                    from quant.ui.renderer import print_confirm_prompt
                    if not print_confirm_prompt("CMD", {"command": command, "type": type}):
                        return ToolResult(False, {}, error="Cancelled by user.")

        if type == "python":
            return self._run_python(command)
        return self._run_shell(command, cwd, timeout)

    def _run_shell(self, command: str, cwd_str: str, timeout: int) -> ToolResult:
        for pattern in BLOCKED:
            if re.search(pattern, command, re.IGNORECASE):
                return ToolResult(False, {"command": command},
                                  error="Blocked: dangerous command pattern")

        # Используем рабочую директорию агента если не указана явно
        if cwd_str:
            from quant.tools.filesystem import _fix_path
            cwd = _fix_path(cwd_str)
        else:
            cwd = get_working_dir()

        try:
            is_win = sys.platform == "win32"
            result = subprocess.run(
                command if is_win else shlex.split(command),
                shell=is_win,
                capture_output=True,
                text=True,
                cwd=str(cwd),
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            stdout = (result.stdout or "").strip()[:4000]
            stderr = (result.stderr or "").strip()[:1000]
            return ToolResult(
                success=result.returncode == 0,
                data={
                    "stdout":     stdout,
                    "stderr":     stderr,
                    "returncode": result.returncode,
                    "cwd":        str(cwd),
                },
                error=stderr if result.returncode != 0 and not stdout else None,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, {}, error=f"Timeout after {timeout}s")
        except FileNotFoundError as e:
            return ToolResult(False, {}, error=f"Command not found: {e}")
        except Exception as e:
            return ToolResult(False, {}, error=str(e))

    def _run_python(self, code: str) -> ToolResult:
        import os
        import types
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        safe_builtins = {
            "__name__": "__quant_exec__",
            "__doc__": None,
            "__build_class__": __builtins__.__build_class__ if hasattr(__builtins__, '__build_class__') else __builtins__['__build_class__'] if isinstance(__builtins__, dict) else None,
            "__import__": self._restricted_import,
            "print": print,
            "len": len,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "type": type,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
            "reversed": reversed,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "repr": repr,
            "format": format,
            "iter": iter,
            "next": next,
            "open": open,
            "True": True,
            "False": False,
            "None": None,
        }
        if isinstance(__builtins__, dict):
            safe_builtins.update({k: v for k, v in __builtins__.items() if k.startswith('_') and k != '__name__'})

        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                exec(compile(code, "<quant>", "exec"), {"__builtins__": safe_builtins})
            return ToolResult(True, {
                "output": stdout_buf.getvalue()[:4000],
                "stderr": stderr_buf.getvalue()[:500],
                "type":   "python",
            })
        except Exception:
            return ToolResult(False, {"type": "python"},
                              error=traceback.format_exc()[-2000:])

    @staticmethod
    def _restricted_import(name, *args, **kwargs):
        BLOCKED_MODULES = {"os", "subprocess", "shutil", "sys", "signal",
                           "socket", "multiprocessing", "threading", "ctypes"}
        top = name.split(".")[0]
        if top in BLOCKED_MODULES:
            raise ImportError(f"Import of '{name}' is blocked in quant exec sandbox.")
        return __builtins__.__import__(name, *args, **kwargs) if hasattr(__builtins__, '__import__') else __builtins__['__import__'](name, *args, **kwargs)
