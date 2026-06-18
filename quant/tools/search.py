"""QUANT CLI — SEARCH tool (ripgrep with grep fallback)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from quant.tools.base import BaseTool, ToolResult


class SearchTool(BaseTool):
    name = "SEARCH"
    description = "Search for text patterns in files using ripgrep (or grep as fallback)."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search pattern (regex supported)"},
            "path": {"type": "string", "description": "Directory to search (default: current dir)"},
            "file_pattern": {"type": "string", "description": "File glob pattern (e.g. '*.py')"},
            "case_sensitive": {"type": "boolean", "description": "Case-sensitive search (default: False)"},
            "max_results": {"type": "integer", "description": "Max results to return (default: 50)"},
        },
        "required": ["query"],
    }

    async def execute(
        self,
        query: str,
        path: str = ".",
        file_pattern: str = "",
        case_sensitive: bool = False,
        max_results: int = 50,
    ) -> ToolResult:
        search_path = Path(path).resolve()

        if shutil.which("rg"):
            cmd = ["rg", "--line-number", "--no-heading", "--color=never"]
            if not case_sensitive:
                cmd.append("-i")
            if file_pattern:
                cmd.extend(["--glob", file_pattern])
            cmd.extend(["-m", str(max_results), query, str(search_path)])
        else:
            cmd = ["grep", "-rn", "--include", file_pattern or "*"]
            if not case_sensitive:
                cmd.append("-i")
            cmd.extend([query, str(search_path)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            lines = result.stdout.strip().splitlines()[:max_results]
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "matches": lines,
                    "count": len(lines),
                    "truncated": len(lines) >= max_results,
                },
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, data={}, error="Search timed out")
        except Exception as e:
            return ToolResult(success=False, data={}, error=str(e))
