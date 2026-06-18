"""QUANT CLI — FILESYSTEM tool с правильными Windows путями и подтверждением."""
from __future__ import annotations
import os
import shutil
import sys
from pathlib import Path, PureWindowsPath
from quant.tools.base import BaseTool, ToolResult


def _fix_path(raw: str) -> Path:
    """
    Исправляем пути которые LLM передаёт с битыми слэшами.
    Например: 'C:UserssstprDesktop\\test' → 'C:\\Users\\sstpr\\Desktop\\test'
    """
    if not raw:
        return Path(".")

    if sys.platform == "win32" and len(raw) >= 2 and raw[1] == ":":
        if len(raw) >= 3 and raw[2] in ("/", "\\"):
            normalized = raw.replace("/", "\\")
            return Path(normalized)

        body = raw[2:]
        if "\\" not in body and "/" not in body and len(body) > 0:
            fixed = _reconstruct_win_path(raw[0], body)
            if fixed:
                return fixed

        fixed = raw[0] + ":\\" + body.lstrip("\\/")
        return Path(fixed)

    normalized = raw.replace("\\\\", "/").replace("\\", "/")
    return Path(normalized)


def _reconstruct_win_path(drive: str, body: str) -> Path | None:
    KNOWN_DIRS = [
        "Users", "Windows", "Program Files", "Program Files (x86)",
        "ProgramData", "AppData", "Desktop", "Documents", "Downloads",
    ]
    for d in KNOWN_DIRS:
        idx = body.lower().find(d.lower())
        if idx > 0:
            before = body[:idx]
            after = body[idx + len(d):]
            candidate = f"{drive}:\\{before}\\{d}\\{after}"
            candidate = candidate.replace("/", "\\")
            p = Path(candidate)
            if p.exists():
                return p

    candidate = f"{drive}:\\{body}"
    candidate = candidate.replace("/", "\\")
    p = Path(candidate)
    if p.exists():
        return p

    return None


def _resolve(raw: str, cwd: Path) -> Path:
    """Резолвим путь относительно рабочей директории если он не абсолютный."""
    p = _fix_path(raw)
    if not p.is_absolute():
        p = cwd / p
    return p


# Глобальная CWD (устанавливается из cli.py при запуске)
_WORKING_DIR: Path = Path.cwd()

def set_working_dir(path: Path) -> None:
    global _WORKING_DIR
    _WORKING_DIR = path

def get_working_dir() -> Path:
    return _WORKING_DIR


class FilesystemTool(BaseTool):
    name = "FILESYSTEM"
    description = (
        "Perform file system operations on the user's machine. "
        "IMPORTANT: Always use forward slashes in paths (e.g. 'C:/Users/test' or just 'subfolder/name'). "
        "Relative paths are resolved from the current working directory. "
        "Actions: mkdir=create folder, list=show contents, delete=remove, "
        "copy=duplicate, move=move/rename, exists=check if path exists, cwd=show current directory."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["mkdir", "list", "delete", "copy", "move", "exists", "cwd"],
                "description": "Operation: mkdir/list/delete/copy/move/exists/cwd",
            },
            "path": {
                "type": "string",
                "description": "Path to file/folder. Use forward slashes. Relative = from working dir.",
            },
            "destination": {
                "type": "string",
                "description": "Destination path for copy/move operations.",
            },
        },
        "required": ["action"],
    }

    async def execute(self, action: str, path: str = ".", destination: str = "", **kwargs) -> ToolResult:
        from quant.tools.safety import is_path_blocked, is_outside_project
        cwd = get_working_dir()

        if action == "cwd":
            entries = []
            try:
                for item in sorted(cwd.iterdir()):
                    entries.append({
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                    })
            except Exception:
                pass
            return ToolResult(True, {
                "current_directory": str(cwd),
                "contents": entries,
                "count": len(entries),
            })

        p = _resolve(path, cwd)

        blocked, reason = is_path_blocked(str(p))
        if blocked:
            return ToolResult(False, {}, error=f"BLOCKED: {reason}")

        outside, warning = is_outside_project(str(p), str(cwd))
        if outside and action in ("delete", "move"):
            return ToolResult(False, {}, error=f"BLOCKED: {warning}")

        if destination:
            dst = _resolve(destination, cwd)
            blocked, reason = is_path_blocked(str(dst))
            if blocked:
                return ToolResult(False, {}, error=f"BLOCKED: {reason}")

        if action == "exists":
            return ToolResult(True, {
                "path":   str(p),
                "exists": p.exists(),
                "type":   "dir" if p.is_dir() else "file" if p.is_file() else "none",
            })

        if action == "mkdir":
            try:
                p.mkdir(parents=True, exist_ok=True)
                return ToolResult(True, {
                    "created": str(p),
                    "action":  "mkdir",
                })
            except Exception as e:
                return ToolResult(False, {}, error=f"Cannot create folder: {e}")

        if action == "list":
            if not p.exists():
                return ToolResult(False, {}, error=f"Path not found: {p}\nWorking dir: {cwd}")
            try:
                entries = []
                for item in sorted(p.iterdir()):
                    size = item.stat().st_size if item.is_file() else 0
                    entries.append({
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "size": size,
                    })
                return ToolResult(True, {
                    "path":    str(p),
                    "entries": entries,
                    "count":   len(entries),
                })
            except Exception as e:
                return ToolResult(False, {}, error=str(e))

        if action == "delete":
            if not p.exists():
                return ToolResult(False, {}, error=f"Not found: {p}")
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                return ToolResult(True, {"deleted": str(p)})
            except Exception as e:
                return ToolResult(False, {}, error=str(e))

        if action in ("copy", "move"):
            if not destination:
                return ToolResult(False, {}, error=f"'{action}' requires destination")
            dst = _resolve(destination, cwd)
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                if action == "copy":
                    shutil.copytree(p, dst) if p.is_dir() else shutil.copy2(p, dst)
                else:
                    shutil.move(str(p), str(dst))
                return ToolResult(True, {"action": action, "from": str(p), "to": str(dst)})
            except Exception as e:
                return ToolResult(False, {}, error=str(e))

        return ToolResult(False, {}, error=f"Unknown action: {action}")
