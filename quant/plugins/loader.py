"""QUANT CLI — Plugin loader."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path


def load_plugins(plugin_dir: Path | None = None) -> list:
    if plugin_dir is None:
        plugin_dir = Path(".quant") / "plugins"

    if not plugin_dir.exists():
        return []

    tools = []
    for py_file in sorted(plugin_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"quant_plugin_{py_file.stem}", str(py_file)
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)

            if hasattr(mod, "register"):
                result = mod.register()
                if isinstance(result, list):
                    tools.extend(result)
                elif result is not None:
                    tools.append(result)
        except Exception as e:
            print(f"Plugin load error {py_file.name}: {e}")

    return tools
