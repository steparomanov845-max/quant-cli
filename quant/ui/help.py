"""QUANT CLI — Help system (with i18n)."""
from quant.ui.i18n import t


def get_help_text(section: str = "") -> str:
    if section and section in ("commands", "modes", "tools", "hotkeys", "safety"):
        return _get_section(section)

    lines = []
    for s in ["commands", "modes", "tools", "hotkeys", "safety"]:
        lines.append(_get_section(s))
    return "\n\n".join(lines)


def _get_section(name: str) -> str:
    lines = []
    lines.append(f"  [bold #bf5fff]{t(f'help_{name}')}[/]")
    lines.append(f"  {'─' * 44}")

    items = _get_items(name)
    for key, val in items.items():
        lines.append(f"  [bold #ff79c6]{key:<26}[/] [white]{val}[/]")
    return "\n".join(lines)


def _get_items(name: str) -> dict:
    if name == "commands":
        return {
            "/help [section]": t("cmd_help"),
            "/clear": t("cmd_clear"),
            "/status": t("cmd_status"),
            "/tokens": t("cmd_tokens"),
            "/mode <name>": t("cmd_mode"),
            "/model [auto]": t("cmd_model"),
            "/confirm on|off|allow": t("cmd_confirm"),
            "/restore <file>": t("cmd_restore"),
            "/export [file]": t("cmd_export"),
            "/theme <name>": t("cmd_theme"),
            "/lang <name>": t("cmd_lang"),
            "/exit": t("cmd_exit"),
        }
    elif name == "modes":
        return {
            "chat": t("mode_chat_d"),
            "agent": t("mode_agent_d"),
            "debug": t("mode_debug_d"),
            "arch": t("mode_arch_d"),
            "refactor": t("mode_refactor_d"),
            "research": t("mode_research_d"),
        }
    elif name == "tools":
        return {
            "READ_FILE": t("tool_read_file"),
            "WRITE_FILE": t("tool_write_file"),
            "EDIT_FILE": t("tool_edit_file"),
            "CMD": t("tool_cmd"),
            "FILESYSTEM": t("tool_filesystem"),
            "SEARCH": t("tool_search"),
            "GIT": t("tool_git"),
            "MEMORY": t("tool_memory"),
            "DATETIME": t("tool_datetime"),
            "WEB_SEARCH": t("tool_web_search"),
            "READ_URL": t("tool_read_url"),
            "PROCESS": t("tool_process"),
        }
    elif name == "hotkeys":
        return {
            "Ctrl+C": t("hk_exit"),
            "Escape": t("hk_stop"),
            "Ctrl+L": t("hk_clear"),
            "Tab": t("hk_tab"),
            "Ctrl+V": t("hk_paste"),
            "Ctrl+Shift+C": t("hk_copy"),
            "Enter": t("hk_enter"),
            "↑/↓": t("hk_arrows"),
        }
    elif name == "safety":
        return {
            t("help_safety"): "",
            "Paths": t("sf_paths"),
            "Commands": t("sf_cmds"),
            "PowerShell": t("sf_ps"),
            "Backups": t("sf_backups"),
            "Restore": t("sf_restore"),
            "Loop": t("sf_loop"),
            "CWD": t("sf_cwd"),
        }
    return {}


COMMANDS_LIST = [
    "/help", "/clear", "/status", "/tokens", "/mode", "/model",
    "/confirm", "/restore", "/export", "/theme", "/lang", "/exit",
]
