"""Example plugin for QUANT CLI.

To use: place this file in .quant/plugins/ directory.
The file must export a register() function that returns tool instances.
"""
from __future__ import annotations
from quant.tools.base import BaseTool, ToolResult


class HashTool(BaseTool):
    name = "HASH"
    description = "Calculate MD5/SHA256 hash of a string."
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to hash"},
            "algorithm": {"type": "string", "enum": ["md5", "sha256"], "description": "Hash algorithm (default: sha256)"},
        },
        "required": ["text"],
    }

    async def execute(self, text: str, algorithm: str = "sha256", **kwargs) -> ToolResult:
        import hashlib
        if algorithm == "md5":
            h = hashlib.md5(text.encode()).hexdigest()
        else:
            h = hashlib.sha256(text.encode()).hexdigest()
        return ToolResult(True, {"algorithm": algorithm, "hash": h})


def register():
    return HashTool()
