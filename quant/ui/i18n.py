"""QUANT CLI — Localization (RU/EN)."""

LANGS = {
    "en": {
        "splash_init": "Initializing core...",
        "splash_tools": "Loading tool registry...",
        "splash_connect": "Connecting to LM Studio...",
        "splash_model": "Detecting model...",
        "splash_context": "Building context engine...",
        "splash_safety": "Loading safety filters...",
        "splash_ready": "Ready",
        "splash_model_label": "model",
        "splash_ctx_label": "ctx",
        "splash_tokens": "tokens",
        "mode_chat": "Default mode. Answer questions, help with tasks.",
        "mode_agent": "Autonomous mode. Executes multi-step tasks without asking.",
        "mode_debug": "Debugging mode. Systematic root-cause analysis.",
        "mode_arch": "Architecture mode. Design and build project structures.",
        "mode_refactor": "Refactor mode. Improve code quality without changing behavior.",
        "mode_research": "Research mode. Deep investigation and analysis.",
        "confirm_approved": "Approved",
        "confirm_denied": "Denied",
        "confirm_always": "Approved (Always Allow)",
        "confirm_waiting": "Waiting for confirmation...",
        "confirm_header": "CONFIRM ACTION",
        "confirm_hint": "↑↓ navigate  •  Enter select",
        "interrupted": "⚠ Interrupted by user",
        "loop_detected": "⚠ Loop detected: same tool called 3 times with same args. Try a different approach.",
        "context_pruned": "Context pruned: removed {n} old messages",
        "export_done": "Exported to {file}",
        "export_error": "Export failed: {error}",
        "theme_changed": "Theme → {name}",
        "lang_changed": "Language → {name}",
        "help_title": "QUANT HELP",
        "summary_title": "QUANTUM MISSION REPORT",
        "summary_runtime": "⏱️  Runtime",
        "summary_tools": "⚒️  Tool calls",
        "summary_backups": "💾  Backups created",
        "summary_tokens": "🧠  Tokens used",
        "summary_status": "🚀  Status",
        "summary_completed": "Task completed successfully",
        "slogan": "Your AI. Your Rules. Your Data stays with you.",
        "help_commands": "COMMANDS",
        "help_modes": "MODES",
        "help_tools": "TOOLS",
        "help_hotkeys": "HOTKEYS",
        "help_safety": "SAFETY",
        "cmd_help": "Show help (commands, modes, tools, hotkeys, safety)",
        "cmd_clear": "Clear chat history",
        "cmd_status": "System status (CPU, RAM, provider)",
        "cmd_tokens": "Token usage for current session",
        "cmd_mode": "Switch mode: chat | agent | debug | arch | refactor | research",
        "cmd_model": "List models / auto-detect / switch",
        "cmd_confirm": "Toggle confirmations or session auto-approve",
        "cmd_restore": "Restore file from .bak backup",
        "cmd_export": "Export chat to markdown",
        "cmd_theme": "Switch theme: dark | purple | neon",
        "cmd_lang": "Switch language: en | ru",
        "cmd_exit": "Exit QUANT (shows session summary)",
        "mode_chat_d": "Default. Answer questions, help with tasks.",
        "mode_agent_d": "Autonomous. Executes tasks without asking.",
        "mode_debug_d": "Debugging. Systematic root-cause analysis.",
        "mode_arch_d": "Architecture. Design project structures.",
        "mode_refactor_d": "Refactor. Improve code quality.",
        "mode_research_d": "Research. Deep investigation.",
        "tool_read_file": "Read file contents from disk",
        "tool_write_file": "Create or overwrite files (auto-backup)",
        "tool_edit_file": "Find & replace in files (auto-backup)",
        "tool_cmd": "Execute shell commands or Python code",
        "tool_filesystem": "mkdir, list, delete, copy, move, exists, cwd",
        "tool_search": "Search text/regex across files",
        "tool_git": "Git: status, diff, log, commit, branch",
        "tool_memory": "Persistent key-value store",
        "tool_datetime": "Current date and time",
        "tool_web_search": "Search web (DuckDuckGo, up to 15 results)",
        "tool_read_url": "Fetch and read any webpage",
        "tool_process": "System process management",
        "hk_exit": "Exit QUANT",
        "hk_stop": "Stop current agent task",
        "hk_clear": "Clear chat log",
        "hk_tab": "Toggle focus sidebar/input",
        "hk_paste": "Paste from clipboard",
        "hk_copy": "Copy last message from chat",
        "hk_enter": "Submit message",
        "hk_arrows": "Navigate RadioSet options",
        "sf_paths": "System32, Program Files, AppData\\Microsoft",
        "sf_cmds": "pip uninstall, shutdown, del /s, bcdedit, iex",
        "sf_ps": "-EncodedCommand, Invoke-Expression, iex",
        "sf_backups": "WRITE/EDIT create .bak before changes",
        "sf_restore": "/restore <file> to rollback",
        "sf_loop": "Same tool 3x with same args = auto-stop",
        "sf_cwd": "delete/move outside project blocked",
    },
    "ru": {
        "splash_init": "Инициализация ядра...",
        "splash_tools": "Загрузка реестра инструментов...",
        "splash_connect": "Подключение к LM Studio...",
        "splash_model": "Определение модели...",
        "splash_context": "Построение контекстного движка...",
        "splash_safety": "Загрузка фильтров безопасности...",
        "splash_ready": "Готово",
        "splash_model_label": "модель",
        "splash_ctx_label": "контекст",
        "splash_tokens": "токенов",
        "mode_chat": "Режим по умолчанию. Ответы на вопросы, помощь с задачами.",
        "mode_agent": "Автономный режим. Выполняет многошаговые задачи без вопросов.",
        "mode_debug": "Режим отладки. Систематический поиск корневой причины.",
        "mode_arch": "Режим архитектуры. Проектирование и создание структуры проекта.",
        "mode_refactor": "Режим рефакторинга. Улучшение качества кода без изменения поведения.",
        "mode_research": "Режим исследований. Глубокий анализ и изучение.",
        "confirm_approved": "Разрешено",
        "confirm_denied": "Отклонено",
        "confirm_always": "Разрешено (Всегда)",
        "confirm_waiting": "Ожидание подтверждения...",
        "confirm_header": "ПОДТВЕРЖДЕНИЕ ДЕЙСТВИЯ",
        "confirm_hint": "↑↓ навигация  •  Enter выбор",
        "interrupted": "⚠ Прервано пользователем",
        "loop_detected": "⚠ Обнаружено зацикливание: один инструмент вызван 3 раза с теми же аргументами. Попробуйте другой подход.",
        "context_pruned": "Контекст сжат: удалено {n} старых сообщений",
        "export_done": "Экспортировано в {file}",
        "export_error": "Ошибка экспорта: {error}",
        "theme_changed": "Тема → {name}",
        "lang_changed": "Язык → {name}",
        "help_title": "СПРАВКА QUANT",
        "summary_title": "ОТЧЁТ МИССИИ QUANTUM",
        "summary_runtime": "⏱️  Время работы",
        "summary_tools": "⚒️  Вызовов инструментов",
        "summary_backups": "💾  Создано бэкапов",
        "summary_tokens": "🧠  Потрачено токенов",
        "summary_status": "🚀  Статус",
        "summary_completed": "Задача успешно выполнена",
        "slogan": "Твой ИИ. Твои правила. Твои данные остаются с тобой.",
        "help_commands": "КОМАНДЫ",
        "help_modes": "РЕЖИМЫ",
        "help_tools": "ИНСТРУМЕНТЫ",
        "help_hotkeys": "ГОРЯЧИЕ КЛАВИШИ",
        "help_safety": "БЕЗОПАСНОСТЬ",
        "cmd_help": "Показать справку (команды, режимы, инструменты, клавиши, безопасность)",
        "cmd_clear": "Очистить историю чата",
        "cmd_status": "Системный статус (CPU, RAM, провайдер)",
        "cmd_tokens": "Использование токенов за сессию",
        "cmd_mode": "Переключить режим: chat | agent | debug | arch | refactor | research",
        "cmd_model": "Список моделей / автоопределение / переключение",
        "cmd_confirm": "Вкл/выкл подтверждений или авто-разрешение",
        "cmd_restore": "Откат файла из .bak бэкапа",
        "cmd_export": "Экспорт чата в markdown",
        "cmd_theme": "Переключить тему: dark | purple | neon",
        "cmd_lang": "Переключить язык: en | ru",
        "cmd_exit": "Выход с отчётом о сессии",
        "mode_chat_d": "По умолчанию. Ответы на вопросы, помощь.",
        "mode_agent_d": "Автономный. Выполняет задачи без вопросов.",
        "mode_debug_d": "Отладка. Поиск корневой причины.",
        "mode_arch_d": "Архитектура. Проектирование структуры.",
        "mode_refactor_d": "Рефакторинг. Улучшение качества кода.",
        "mode_research_d": "Исследования. Глубокий анализ.",
        "tool_read_file": "Чтение файлов с диска",
        "tool_write_file": "Создание/перезапись файлов (с бэкапом)",
        "tool_edit_file": "Точечные правки find & replace (с бэкапом)",
        "tool_cmd": "Выполнение shell-команд и Python-кода",
        "tool_filesystem": "mkdir, list, delete, copy, move, exists, cwd",
        "tool_search": "Поиск текста/regex по файлам",
        "tool_git": "Git: status, diff, log, commit, branch",
        "tool_memory": "Key-value хранилище между сессиями",
        "tool_datetime": "Текущая дата и время",
        "tool_web_search": "Поиск в интернете (DuckDuckGo, до 15)",
        "tool_read_url": "Чтение веб-страниц как текст",
        "tool_process": "Управление процессами системы",
        "hk_exit": "Выход из QUANT",
        "hk_stop": "Остановка текущей задачи агента",
        "hk_clear": "Очистка чата",
        "hk_tab": "Переключение фокуса sidebar/input",
        "hk_paste": "Вставка из буфера обмена",
        "hk_copy": "Копирование последнего сообщения",
        "hk_enter": "Отправка сообщения",
        "hk_arrows": "Навигация по RadioSet",
        "sf_paths": "System32, Program Files, AppData\\Microsoft",
        "sf_cmds": "pip uninstall, shutdown, del /s, bcdedit, iex",
        "sf_ps": "-EncodedCommand, Invoke-Expression, iex",
        "sf_backups": "WRITE/EDIT создают .bak перед изменениями",
        "sf_restore": "/restore <файл> для отката",
        "sf_loop": "Один инструмент 3x с теми же аргументами = стоп",
        "sf_cwd": "delete/move вне проекта заблокированы",
    },
}

_current_lang = "en"


def t(key: str, **kwargs) -> str:
    text = LANGS.get(_current_lang, LANGS["en"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def set_lang(lang: str):
    global _current_lang
    if lang in LANGS:
        _current_lang = lang
        try:
            from quant.core.config import QuantConfig
            cfg = QuantConfig.load()
            cfg.lang = lang
            cfg.save()
        except Exception:
            pass


def get_lang() -> str:
    return _current_lang


def list_langs() -> list[str]:
    return list(LANGS.keys())


def load_lang_from_config():
    global _current_lang
    try:
        from quant.core.config import QuantConfig
        cfg = QuantConfig.load()
        if cfg.lang in LANGS:
            _current_lang = cfg.lang
    except Exception:
        pass
