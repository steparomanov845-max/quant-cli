"""QUANT CLI — Tool registry."""
from quant.tools.read_file     import ReadFileTool
from quant.tools.write_file    import WriteFileTool
from quant.tools.edit_file     import EditFileTool
from quant.tools.cmd           import CmdTool
from quant.tools.git_tool      import GitTool
from quant.tools.search        import SearchTool
from quant.tools.memory        import MemoryTool
from quant.tools.filesystem    import FilesystemTool
from quant.tools.datetime_tool import DatetimeTool
from quant.tools.web_search    import WebSearchTool
from quant.tools.read_url      import ReadURLTool
from quant.tools.process_tool  import ProcessTool

TOOL_REGISTRY = {
    "READ_FILE":  ReadFileTool,
    "WRITE_FILE": WriteFileTool,
    "EDIT_FILE":  EditFileTool,
    "CMD":        CmdTool,
    "GIT":        GitTool,
    "SEARCH":     SearchTool,
    "MEMORY":     MemoryTool,
    "FILESYSTEM": FilesystemTool,
    "DATETIME":   DatetimeTool,
    "WEB_SEARCH": WebSearchTool,
    "READ_URL":   ReadURLTool,
    "PROCESS":    ProcessTool,
}

DEFAULT_TOOLS = list(TOOL_REGISTRY.keys())

def get_tools(names: list[str] | None = None):
    names = names or DEFAULT_TOOLS
    builtin = [TOOL_REGISTRY[n]() for n in names if n in TOOL_REGISTRY]

    from quant.plugins.loader import load_plugins
    from pathlib import Path
    plugin_tools = load_plugins(Path(".quant") / "plugins")
    for t in plugin_tools:
        if hasattr(t, 'name'):
            TOOL_REGISTRY[t.name] = t.__class__
    builtin.extend(plugin_tools)

    return builtin
