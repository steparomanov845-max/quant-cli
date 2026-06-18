# QUANT CLI 3.0 — Полная документация

**Your AI. Your Rules. Your Data stays with you.**

---

## Что нового в 3.0

### Интерфейс (TUI)
- **Space Cyberpunk дизайн** — глубокий космический фиолетовый с неоновыми акцентами
- **3-зонный лейаут:** Sidebar (статус) + Workspace (чат) + StatusBar (внизу)
- **Splash Screen** — анимированный приветственный экран с прогресс-баром (70-120ms задержки)
- **Streaming** — ответы отображаются по мере генерации токенов
- **CPU/RAM монитор** — обновляется каждые 3 секунды в sidebar
- **Подсказки команд** — при вводе `/` в статус-баре показываются совпадающие команды

### Slash-команды
| Команда | Описание |
|---------|----------|
| `/help [section]` | Подробная справка (commands, modes, tools, hotkeys, safety) |
| `/clear` | Очистить историю чата |
| `/status` | Системный статус (CPU, RAM, провайдер) |
| `/tokens` | Использование токенов |
| `/mode <name>` | Переключение режима (chat, agent, debug, arch, refactor, research) |
| `/model [auto]` | Список моделей / автоопределение / переключение |
| `/confirm on\|off\|allow` | Вкл/выкл подтверждений или авто-разрешение на сессию |
| `/restore <file>` | Откат файла из .bak бэкапа |
| `/export [file]` | Экспорт чата в markdown |
| `/theme <name>` | Переключение темы (dark, purple, neon) |
| `/lang <name>` | Переключение языка (en, ru) |
| `/exit` | Выход с отчётом о сессии |

### Режимы работы
| Режим | Описание |
|-------|----------|
| `chat` | По умолчанию. Ответы на вопросы, помощь с задачами |
| `agent` | Автономный. Выполняет многошаговые задачи без вопросов |
| `debug` | Отладка. Систематический поиск корневой причины |
| `arch` | Архитектура. Проектирование и создание структуры проекта |
| `refactor` | Рефакторинг. Улучшение качества кода |
| `research` | Исследования. Глубокий анализ и изучение |

---

## Инструменты (12 встроенных + Plugin API)

### Файловые операции
| Инструмент | Описание |
|------------|----------|
| `READ_FILE` | Чтение файлов с диска |
| `WRITE_FILE` | Создание/перезапись файлов (с автоматическим бэкапом) |
| `EDIT_FILE` | Точечные правки find & replace (с автоматическим бэкапом) |
| `FILESYSTEM` | mkdir, list, delete, copy, move, exists, cwd |

### Системные
| Инструмент | Описание |
|------------|----------|
| `CMD` | Выполнение shell-команд и Python-кода |
| `GIT` | git status, diff, log, commit, branch, add |
| `SEARCH` | Поиск текста/regex по файлам |
| `PROCESS` | CPU%, RAM, список процессов, порты |

### Веб и данные
| Инструмент | Описание |
|------------|----------|
| `WEB_SEARCH` | Поиск в интернете (DuckDuckGo, до 15 результатов) |
| `READ_URL` | Чтение веб-страниц как текст (всегда использовать после WEB_SEARCH) |
| `MEMORY` | Key-value хранилище между сессиями |
| `DATETIME` | Текущая дата и время |

---

## Безопасность (Safety Core)

### Заблокированные пути (Windows)
- `C:\Windows`, `C:\Windows\System32`, `C:\Windows\SysWOW64`
- `C:\Program Files`, `C:\Program Files (x86)`
- `C:\ProgramData`
- `AppData\Local\Microsoft`, `AppData\Roaming\Microsoft`
- `NTUSER.DAT`, `D:\Windows`, `E:\Windows`, `F:\Windows`

### Заблокированные команды
- **Удаление пакетов:** `pip uninstall`, `pip3 uninstall`, `python -m pip uninstall`
- **Массовое удаление:** `del /s`, `del /q`, `rmdir /s`, `rmdir /q`
- **Права доступа:** `takeown`, `icacls C:\`
- **Системные:** `bcdedit`, `reg delete`, `sc delete`, `net user`
- **Питание:** `shutdown`, `restart`
- **Утилиты:** `sfc /scannow`, `dism`, `cipher /w`
- **PowerShell обфускация:** `-EncodedCommand`, `-e`, `Invoke-Expression`, `iex`, `Invoke-Command -ScriptBlock`
- **Linux:** `rm -rf /`, `format`, `diskpart`, `mkfs`

### Теневой бэкап
- Автоматически создаёт `.bak` перед `WRITE_FILE` и `EDIT_FILE`
- Бэки хранятся в `~/.quant/backups/`
- Откат: `/restore <путь_к_файлу>`

### Защита от зацикливания
- Если агент 3 раза подряд вызывает один инструмент с теми же аргументами → принудительная остановка
- Сообщение: `⚠ Loop detected: same tool called 3 times with same args`

### Предупреждения
- Блокировка `delete` и `move` если путь вне проекта (CWD protection)
- Подтверждение через RadioSet (стрелки + Enter)

---

## Провайдеры

| Провайдер | Описание |
|-----------|----------|
| **LM Studio** | По умолчанию. Автоопределение модели и контекста через v0 API |
| **OpenAI** | GPT через API (требует API-ключ) |
| **DeepSeek** | DeepSeek через API (требует API-ключ) |

### Auto-retry
- LM Studio автоматически повторяет запрос 3 раза при ошибках HTTP
- Экспоненциальная задержка: 1с → 2с → 3с
- Если все попытки неудачны → возврат ошибки

---

## Streaming и контекст

### Streaming ответов
- Токены отображаются по мере генерации
- Статус-бар показывает `Streaming...`
- Агент вызывает `on_token` callback для каждого токена

### Контекстное сжатие
- Автоматическое удаление старых tool-сообщений при приближении к лимиту (85%)
- Уведомление в чате: `Context pruned: removed N old messages`
- Сохраняются последние 10 сообщений и первые 10 tool-вызовов

---

## UX улучшения

### Клавиатура
| Комбинация | Действие |
|------------|----------|
| `Ctrl+C` | Выход из QUANT |
| `Escape` | Принудительная остановка агента |
| `Ctrl+L` | Очистка чата |
| `Tab` | Переключение фокуса между sidebar и input |
| `Ctrl+V` | Вставка из буфера обмена |
| `Ctrl+Shift+C` | Копирование последнего сообщения из чата |
| `Enter` | Отправка сообщения |
| `↑/↓` | Навигация по RadioSet в подтверждении |

### Подтверждения
- RadioSet с навигацией стрелками и подсветкой
- `y` — разрешить действие
- `n` — отклонить действие
- `a` — разрешить всё до перезапуска сессии
- Оранжевая рамка `#ff6400` для визуального выделения

### Подсказки команд
- При вводе `/` в статус-баре показываются совпадающие команды
- Автоматическое обновление при каждом нажатии клавиши

---

## Темы и локализация

### Темы (`/theme`)
| Тема | Описание |
|------|----------|
| `dark` | Тёмная туманность (по умолчанию) — `#0f0a19` фон |
| `purple` | Глубокий фиолетовый — `#1a0a2e` фон |
| `neon` | Неоновый киберпанк — `#0a0a0a` фон, `#00f5d4` акцент |

### Языки (`/lang`)
| Язык | Описание |
|------|----------|
| `en` | Английский (по умолчанию) |
| `ru` | Русский — все сообщения интерфейса переведены |

---

## Splash Screen

При запуске `quant` отображается анимированный экран:
- ASCII-арт QUANT с градиентом от тёмно-фиолетового к ярко-пурпурному
- Прогресс-бар с этапами инициализации (7 этапов)
- Микро-задержки 70-120ms между строками
- Индикаторы: `⠋⠙⠹⠸` → `✓` на каждом этапе

### Этапы инициализации
1. `Initializing core...`
2. `Loading tool registry...`
3. `Connecting to LM Studio...`
4. `Detecting model...`
5. `Building context engine...`
6. `Loading safety filters...`
7. `Ready`

---

## Session Summary

При `/exit` или завершении большой задачи выводится отчёт:

```
──────────────────────────────────────────────
  QUANTUM MISSION REPORT
──────────────────────────────────────────────
  ⏱️  Runtime              4 min 12 sec
  ⚒️  Tool calls           14
  💾  Backups created      3
  🧠  Tokens used          18,421
  🚀  Status               Task completed successfully
──────────────────────────────────────────────
```

### Отслеживаемые метрики
- **Время работы** — от запуска до `/exit`
- **Вызовы инструментов** — общее количество tool-вызовов
- **Бэкапы** — количество созданных .bak файлов
- **Токены** — общее использование токенов за сессию

---

## Plugin API

### Структура
```
.quant/plugins/
  ├── __init__.py
  ├── loader.py           # Загрузчик плагинов
  └── my_plugin.py        # Ваш плагин
```

### Формат плагина
```python
from quant.tools.base import BaseTool, ToolResult

class MyTool(BaseTool):
    name = "MY_TOOL"
    description = "Описание инструмента для LLM"
    parameters = {
        "type": "object",
        "properties": {
            "arg": {"type": "string", "description": "Аргумент"},
        },
        "required": ["arg"],
    }

    async def execute(self, arg: str, **kwargs) -> ToolResult:
        # Ваша логика
        return ToolResult(True, {"result": "ok"})

def register():
    return MyTool()
```

### Загрузка
- Плагины загружаются из `.quant/plugins/*.py`
- Функция `register()` возвращает экземпляр Tool
- Плагин автоматически добавляется в реестр инструментов
- Поддержка多个 плагинов одновременно

---

## Установка

```bash
git clone <repo>
cd quant-cli
pip install -e .
quant init
# Запусти LM Studio и загрузи модель
quant
```

### Зависимости
- Python ≥ 3.11
- rich, prompt_toolkit, httpx, pydantic-settings, pyyaml
- psutil, typer, duckduckgo-search, textual

---

## Конфигурация

Конфиг: `.quant/config.yaml`

```yaml
provider: lmstudio
model: local-model
context_size: 32768
mode: chat
lmstudio_base_url: http://localhost:1234
lmstudio_timeout: 300
openai_api_key: ""
openai_base_url: https://api.openai.com/v1
deepseek_api_key: ""
deepseek_base_url: https://api.deepseek.com/v1
confirm_actions: true
safe_mode: true
```

---

## Архитектура

```
quant/
├── main.py              # Entry point (Typer CLI)
├── cli.py               # Classic REPL
├── cli_tui.py           # TUI wiring (QuantApp)
├── agent/
│   ├── agent.py         # ReAct loop with streaming + loop detection
│   └── modes/
├── core/
│   ├── config.py        # Pydantic settings + YAML
│   ├── context.py       # System prompt builder (улучшен для READ_URL)
│   └── session.py       # Session with context pruning
├── providers/
│   ├── base.py          # BaseProvider interface
│   ├── lmstudio.py      # LM Studio (auto-detect, retry, streaming)
│   ├── openai.py        # OpenAI API
│   └── deepseek.py      # DeepSeek API
├── tools/
│   ├── base.py          # BaseTool interface
│   ├── safety.py        # Safety filters + backups + PowerShell filter
│   ├── cmd.py, read_file.py, write_file.py, edit_file.py,
│   │   filesystem.py, search.py, git_tool.py, memory.py,
│   │   datetime_tool.py, web_search.py, read_url.py, process_tool.py
│   └── __init__.py      # Tool registry + plugin loader
├── plugins/
│   ├── loader.py        # Plugin loader
│   └── example_hash.py  # Example plugin (HASH tool)
└── ui/
    ├── tui.py           # Textual TUI (3-zone layout, streaming, copy/paste)
    ├── renderer.py      # Rich console renderer (splash, session summary)
    ├── status_bar.py    # /status dashboard
    ├── diff_viewer.py   # Visual diff
    ├── themes.py        # Theme definitions (dark, purple, neon)
    ├── i18n.py          # Localization (EN/RU, 50+ строк)
    └── help.py          # Help system (commands, modes, tools, hotkeys, safety)
```
