"""QUANT CLI — MEMORY tool (.quant/memory.json)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from quant.tools.base import BaseTool, ToolResult

MEMORY_FILE = Path.home() / ".quant" / "memory.json"


def _load() -> dict:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class MemoryTool(BaseTool):
    name = "MEMORY"
    description = "Persistent key-value memory across sessions (.quant/memory.json)."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get", "set", "delete", "list"],
                "description": "Memory operation",
            },
            "key": {"type": "string", "description": "Memory key"},
            "value": {"type": "string", "description": "Value to store (for set)"},
            "ttl": {"type": "integer", "description": "Time-to-live in seconds (optional)"},
        },
        "required": ["action"],
    }

    async def execute(
        self,
        action: str,
        key: str = "",
        value: str = "",
        ttl: int | None = None,
    ) -> ToolResult:
        store = _load()
        now = time.time()

        # Expire TTL entries
        store = {k: v for k, v in store.items()
                 if not isinstance(v, dict) or v.get("expires", now + 1) > now}

        if action == "get":
            entry = store.get(key)
            if entry is None:
                return ToolResult(success=False, data={}, error=f"Key not found: {key}")
            val = entry["value"] if isinstance(entry, dict) else entry
            return ToolResult(success=True, data={"key": key, "value": val})

        elif action == "set":
            entry: dict | str = {"value": value, "updated": now}
            if ttl:
                entry["expires"] = now + ttl
            store[key] = entry
            _save(store)
            return ToolResult(success=True, data={"key": key, "stored": True})

        elif action == "delete":
            if key in store:
                del store[key]
                _save(store)
                return ToolResult(success=True, data={"key": key, "deleted": True})
            return ToolResult(success=False, data={}, error=f"Key not found: {key}")

        elif action == "list":
            keys = list(store.keys())
            return ToolResult(success=True, data={"keys": keys, "count": len(keys)})

        return ToolResult(success=False, data={}, error=f"Unknown action: {action}")
