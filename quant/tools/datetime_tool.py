"""QUANT CLI — DATETIME tool: текущая дата, время, timezone."""
from __future__ import annotations
from datetime import datetime, timezone
from quant.tools.base import BaseTool, ToolResult


class DatetimeTool(BaseTool):
    name = "DATETIME"
    description = (
        "Get current date, time, day of week, month, year, or Unix timestamp. "
        "Use this to know today's date and time."
    )
    parameters = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["full", "date", "time", "timestamp", "iso"],
                "description": (
                    "full = date + time + weekday, "
                    "date = YYYY-MM-DD, "
                    "time = HH:MM:SS, "
                    "timestamp = Unix epoch, "
                    "iso = ISO 8601"
                ),
            }
        },
        "required": [],
    }

    async def execute(self, format: str = "full", **kwargs) -> ToolResult:
        now   = datetime.now()
        now_utc = datetime.now(timezone.utc)

        if format == "date":
            return ToolResult(True, {
                "date": now.strftime("%Y-%m-%d"),
                "day": now.day,
                "month": now.month,
                "month_name": now.strftime("%B"),
                "year": now.year,
                "weekday": now.strftime("%A"),
            })

        elif format == "time":
            return ToolResult(True, {
                "time": now.strftime("%H:%M:%S"),
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
            })

        elif format == "timestamp":
            return ToolResult(True, {
                "unix_timestamp": int(now.timestamp()),
                "utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            })

        elif format == "iso":
            return ToolResult(True, {"iso": now.isoformat()})

        else:  # full (default)
            return ToolResult(True, {
                "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "weekday": now.strftime("%A"),
                "month_name": now.strftime("%B"),
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
