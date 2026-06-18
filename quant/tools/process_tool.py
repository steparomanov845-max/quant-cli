"""QUANT CLI — PROCESS tool: список процессов, kill, системная информация."""
from __future__ import annotations
import sys
from quant.tools.base import BaseTool, ToolResult


class ProcessTool(BaseTool):
    name = "PROCESS"
    description = (
        "Manage system processes and get system info. "
        "Actions: list=show running processes, kill=terminate by PID, "
        "info=CPU/RAM/disk usage, ports=show open network ports."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "kill", "info", "ports"],
                "description": "list=processes, kill=terminate, info=system stats, ports=network",
            },
            "pid": {
                "type": "integer",
                "description": "Process ID (required for kill)",
            },
            "name_filter": {
                "type": "string",
                "description": "Filter processes by name (for list action)",
            },
        },
        "required": ["action"],
    }

    async def execute(self, action: str, pid: int = 0,
                      name_filter: str = "", **kwargs) -> ToolResult:
        try:
            import psutil
        except ImportError:
            return ToolResult(False, {}, error="psutil not installed. Run: pip install psutil")

        if action == "list":
            procs = []
            for p in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_info"]):
                try:
                    info = p.info
                    if name_filter and name_filter.lower() not in info["name"].lower():
                        continue
                    mem_mb = round(info["memory_info"].rss / 1024 / 1024, 1) if info["memory_info"] else 0
                    procs.append({
                        "pid":    info["pid"],
                        "name":   info["name"],
                        "status": info["status"],
                        "cpu%":   info["cpu_percent"],
                        "mem_mb": mem_mb,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            # Сортируем по памяти
            procs.sort(key=lambda x: x["mem_mb"], reverse=True)
            return ToolResult(True, {"processes": procs[:50], "total": len(procs)})

        elif action == "kill":
            if not pid:
                return ToolResult(False, {}, error="pid is required for kill action")
            try:
                p = psutil.Process(pid)
                name = p.name()
                p.terminate()
                return ToolResult(True, {"killed": pid, "name": name})
            except psutil.NoSuchProcess:
                return ToolResult(False, {}, error=f"Process {pid} not found")
            except psutil.AccessDenied:
                return ToolResult(False, {}, error=f"Access denied for PID {pid}")

        elif action == "info":
            import asyncio
            cpu    = psutil.cpu_percent(interval=None)
            await asyncio.sleep(0.5)
            cpu    = psutil.cpu_percent(interval=None)
            mem    = psutil.virtual_memory()
            disk   = psutil.disk_usage("/")
            return ToolResult(True, {
                "cpu_percent":    cpu,
                "ram_total_gb":   round(mem.total / 1024**3, 1),
                "ram_used_gb":    round(mem.used  / 1024**3, 1),
                "ram_percent":    mem.percent,
                "disk_total_gb":  round(disk.total / 1024**3, 1),
                "disk_used_gb":   round(disk.used  / 1024**3, 1),
                "disk_percent":   disk.percent,
                "platform":       sys.platform,
            })

        elif action == "ports":
            conns = []
            for c in psutil.net_connections(kind="inet"):
                if c.status == "LISTEN":
                    try:
                        name = psutil.Process(c.pid).name() if c.pid else "?"
                    except Exception:
                        name = "?"
                    conns.append({
                        "port": c.laddr.port,
                        "pid":  c.pid,
                        "name": name,
                    })
            conns.sort(key=lambda x: x["port"])
            return ToolResult(True, {"listening_ports": conns, "count": len(conns)})

        return ToolResult(False, {}, error=f"Unknown action: {action}")
