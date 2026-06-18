from pathlib import Path
from quant.tools.base import BaseTool, ToolResult

class ReadFileTool(BaseTool):
    name = "READ_FILE"
    description = "Read file contents"
    parameters = {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}

    async def execute(self, path: str, max_lines: int = 500, **kwargs):
        from quant.tools.filesystem import _resolve
        cwd = __import__('quant.tools.filesystem', fromlist=['get_working_dir']).get_working_dir()
        p = _resolve(path, cwd)
        if not p.exists():
            return ToolResult(False, {}, f"File not found: {path}")
        content = p.read_text(encoding="utf-8", errors="replace")[:max_lines*200]
        return ToolResult(True, {"path": str(p), "content": content})
