"""QUANT CLI — Safety restrictions."""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path


BLOCKED_PATHS = [
    r"C:\\Windows",
    r"C:\\Windows\\System32",
    r"C:\\Windows\\SysWOW64",
    r"C:\\Program Files",
    r"C:\\Program Files \(x86\)",
    r"C:\\ProgramData",
    r"C:\\Users\\.*\\AppData\\Local\\Microsoft",
    r"C:\\Users\\.*\\AppData\\Roaming\\Microsoft",
    r"C:\\Users\\.*\\NTUSER\.DAT",
    r"D:\\Windows",
    r"E:\\Windows",
    r"F:\\Windows",
]

BLOCKED_CMD_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"format\s+[a-zA-Z]:",
    r"diskpart",
    r":\(\)\s*\{.*\}",
    r"dd\s+if=.*of=/dev/[sh]d",
    r"mkfs\.",
    r"pip\s+uninstall",
    r"pip3\s+uninstall",
    r"python\s+-m\s+pip\s+uninstall",
    r"del\s+/[sS]",
    r"del\s+/[qQ]",
    r"rmdir\s+/[sS]",
    r"rmdir\s+/[qQ]",
    r"takeown",
    r"icacls\s+C:\\",
    r"bcdedit",
    r"reg\s+delete",
    r"sc\s+delete",
    r"net\s+user",
    r"shutdown",
    r"restart",
    r"sfc\s+/scannow",
    r"dism",
    r"cipher\s+/w",
    r"-EncodedCommand",
    r"Invoke-Expression",
    r"\biex\b",
    r"Invoke-Command\s+-ScriptBlock",
    r"powershell.*-e\s",
    r"cmd\s+/c\s+powershell",
]

BACKUP_DIR = Path.home() / ".quant" / "backups"


def _ensure_backup_dir():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_backup(file_path: Path) -> Path | None:
    if not file_path.exists():
        return None
    _ensure_backup_dir()
    import time
    ts = time.strftime("%Y%m%d_%H%M%S")
    safe_name = str(file_path).replace(":", "_").replace("\\", "_").replace("/", "_")
    backup = BACKUP_DIR / f"{safe_name}.{ts}.bak"
    shutil.copy2(file_path, backup)
    return backup


def restore_latest_backup(file_path: Path) -> tuple[bool, str]:
    safe_name = str(file_path).replace(":", "_").replace("\\", "_").replace("/", "_")
    if not BACKUP_DIR.exists():
        return False, "No backups found"
    backups = sorted(BACKUP_DIR.glob(f"{safe_name}.*.bak"), reverse=True)
    if not backups:
        return False, f"No backups for {file_path}"
    shutil.copy2(backups[0], file_path)
    return True, f"Restored from {backups[0].name}"


def is_path_blocked(path_str: str) -> tuple[bool, str]:
    if sys.platform != "win32":
        return False, ""

    normalized = path_str.replace("/", "\\")
    for pattern in BLOCKED_PATHS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True, f"Access to {pattern} is blocked for safety"
    return False, ""


def is_outside_project(path_str: str, project_root: str) -> tuple[bool, str]:
    if sys.platform != "win32":
        return False, ""

    normalized = path_str.replace("/", "\\")
    root = project_root.replace("/", "\\")
    if not normalized.startswith(root):
        return True, f"Warning: {path_str} is outside project directory"
    return False, ""


def is_cmd_blocked(command: str) -> tuple[bool, str]:
    for pattern in BLOCKED_CMD_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            reason = f"Command matched blocked pattern: {pattern}"
            if "uninstall" in pattern:
                reason = "Uninstalling packages is blocked. Only pip install is allowed."
            if "EncodedCommand" in pattern or "Invoke-Expression" in pattern or "iex" in pattern:
                reason = "PowerShell obfuscation is blocked for safety."
            return True, reason
    return False, ""
