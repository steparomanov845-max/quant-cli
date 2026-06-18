"""QUANT CLI — GIT tool."""
from __future__ import annotations

import subprocess
from pathlib import Path

from quant.tools.base import BaseTool, ToolResult


def _run_git(args: list[str], cwd: str) -> tuple[str, str, int]:
    result = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True,
        cwd=cwd, timeout=30,
        encoding="utf-8", errors="replace",
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class GitTool(BaseTool):
    name = "GIT"
    description = "Git operations: commit, diff, log, branch, status."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["commit", "diff", "log", "status", "branch", "add"],
                "description": "Git action to perform",
            },
            "message": {"type": "string", "description": "Commit message (for commit action)"},
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files to stage (for commit/add). Empty = all.",
            },
            "branch": {"type": "string", "description": "Branch name (for branch action)"},
            "cwd": {"type": "string", "description": "Repository root (default: current dir)"},
        },
        "required": ["action"],
    }

    async def execute(
        self,
        action: str,
        message: str = "",
        files: list[str] | None = None,
        branch: str = "",
        cwd: str = ".",
    ) -> ToolResult:
        cwd = str(Path(cwd).resolve())

        if action == "status":
            out, err, rc = _run_git(["status", "--short"], cwd)
            return ToolResult(success=rc == 0, data={"status": out or "clean"}, error=err or None)

        elif action == "diff":
            out, err, rc = _run_git(["diff", "--stat"], cwd)
            diff, _, _ = _run_git(["diff"], cwd)
            return ToolResult(success=True, data={"stat": out, "diff": diff[:8000]})

        elif action == "log":
            out, err, rc = _run_git(["log", "--oneline", "-10"], cwd)
            return ToolResult(success=rc == 0, data={"log": out}, error=err or None)

        elif action == "add":
            targets = files or ["."]
            out, err, rc = _run_git(["add"] + targets, cwd)
            return ToolResult(success=rc == 0, data={"added": targets}, error=err or None)

        elif action == "commit":
            if not message:
                return ToolResult(success=False, data={}, error="commit requires a message")
            stage_targets = files or ["."]
            _run_git(["add"] + stage_targets, cwd)
            out, err, rc = _run_git(["commit", "-m", message], cwd)
            return ToolResult(success=rc == 0, data={"output": out}, error=err if rc != 0 else None)

        elif action == "branch":
            if branch:
                out, err, rc = _run_git(["checkout", "-b", branch], cwd)
            else:
                out, err, rc = _run_git(["branch", "--show-current"], cwd)
            return ToolResult(success=rc == 0, data={"output": out}, error=err if rc != 0 else None)

        return ToolResult(success=False, data={}, error=f"Unknown git action: {action}")
