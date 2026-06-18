# QUANT CLI 3.0.0 ❤️

```
  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗
 ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝
 ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   
 ██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   
 ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   
  ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝  
```

**QUANT CLI 3.0 — Your AI. Your Rules. Your Data stays with you. ❤️**

---

[Русский](#русский) | [English](#english)

---

## Русский

### Что это?

QUANT CLI — это локальный AI-агент для работы с кодом прямо в терминале. Работает полностью на твоей машине, данные никуда не уходят.

### Возможности

- **Стриминг ответов** — токены появляются по мере генерации модели
- **4 провайдера** — LM Studio, Ollama, OpenAI, DeepSeek
- **12 встроенных инструментов** — файлы, shell, git, веб-поиск, память, процессы
- **6 режимов** — chat, agent, debug, arch, refactor, research
- **Авто-определение модели** — сам находит загруженную модель и контекст
- **i18n** — интерфейс на русском и английском
- **Темы** — dark, purple, neon
- **Плагины** — добавляй свои инструменты
- **Безопасность** — блокировка опасных команд, бэкапы перед изменениями

### Установка

```bash
pip install quant-cli
quant init
quant
```

Из исходников:
```bash
git clone https://github.com/sstpr/quant-cli
cd quant-cli
pip install -e .
quant
```

### Запуск с разными провайдерами

**LM Studio (по умолчанию):**
```bash
# Открой LM Studio, загрузи модель, запусти:
quant
```

**Ollama:**
```bash
ollama pull llama3
quant --provider ollama --model llama3
```

**OpenAI:**
```bash
export QUANT_OPENAI_API_KEY="your-key"
quant --provider openai --model gpt-4o
```

### Команды

| Команда | Описание |
|---------|----------|
| `/help` | Справка |
| `/mode <имя>` | Режим: chat, agent, debug, arch, refactor, research |
| `/model [auto]` | Список моделей / авто-определение |
| `/lang <имя>` | Язык: en, ru |
| `/theme <имя>` | Тема: dark, purple, neon |
| `/confirm on\|off\|allow` | Подтверждения действий |
| `/tokens` | Токены за сессию |
| `/restore <файл>` | Откат из бэкапа |
| `/export [файл]` | Экспорт чата в markdown |
| `/status` | Статус системы |
| `/exit` | Выход с отчётом |

### Инструменты

| Инструмент | Описание |
|------------|----------|
| `READ_FILE` | Чтение файлов |
| `WRITE_FILE` | Создание/перезапись (с бэкапом) |
| `EDIT_FILE` | Точечные правки (с бэкапом) |
| `CMD` | Shell-команды и Python-код |
| `FILESYSTEM` | mkdir, list, delete, copy, move, exists, cwd |
| `SEARCH` | Поиск по файлам (ripgrep) |
| `GIT` | Git операции |
| `MEMORY` | Постоянное хранилище |
| `DATETIME` | Дата и время |
| `WEB_SEARCH` | Поиск в интернете |
| `READ_URL` | Чтение веб-страниц |
| `PROCESS` | Управление процессами |

### Горячие клавиши (TUI)

| Клавиша | Действие |
|---------|----------|
| `Ctrl+C` | Выход |
| `Escape` | Остановить задачу |
| `Ctrl+L` | Очистить чат |
| `Tab` | Переключить фокус |
| `Ctrl+V` | Вставка |
| `Ctrl+Shift+C` | Копирование |

### Безопасность

- Заблокированные системные пути (System32, Program Files)
- Заблокированные опасные команды (rm -rf /, format, shutdown)
- Авто-бэкап перед изменениями файлов
- Команда `/restore` для отката
- Детекция зацикливания

### Тесты

```bash
pip install -e ".[test]"
python -m pytest tests/ -v
```

---

## English

### What is this?

QUANT CLI is a local AI coding agent that works directly in your terminal. Runs 100% on your machine — your data never leaves your computer.

### Features

- **Streaming responses** — tokens appear in real-time as the model generates them
- **4 providers** — LM Studio, Ollama, OpenAI, DeepSeek
- **12 built-in tools** — files, shell, git, web search, memory, processes
- **6 modes** — chat, agent, debug, arch, refactor, research
- **Auto-detection** — finds your loaded model and context size automatically
- **i18n** — English and Russian interface
- **Themes** — dark, purple, neon
- **Plugins** — add your own custom tools
- **Safety** — blocks dangerous commands, auto-backup before changes

### Installation

```bash
pip install quant-cli
quant init
quant
```

From source:
```bash
git clone https://github.com/sstpr/quant-cli
cd quant-cli
pip install -e .
quant
```

### Running with different providers

**LM Studio (default):**
```bash
# Open LM Studio, load a model, then run:
quant
```

**Ollama:**
```bash
ollama pull llama3
quant --provider ollama --model llama3
```

**OpenAI:**
```bash
export QUANT_OPENAI_API_KEY="your-key"
quant --provider openai --model gpt-4o
```

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/mode <name>` | Switch mode: chat, agent, debug, arch, refactor, research |
| `/model [auto]` | List models / auto-detect / switch |
| `/lang <name>` | Switch language: en, ru |
| `/theme <name>` | Switch theme: dark, purple, neon |
| `/confirm on\|off\|allow` | Toggle confirmations |
| `/tokens` | Token usage for session |
| `/restore <file>` | Restore from backup |
| `/export [file]` | Export chat to markdown |
| `/status` | System status |
| `/exit` | Exit with session summary |

### Tools

| Tool | Description |
|------|-------------|
| `READ_FILE` | Read file contents |
| `WRITE_FILE` | Create or overwrite files (auto-backup) |
| `EDIT_FILE` | Find & replace in files (auto-backup) |
| `CMD` | Shell commands or Python code |
| `FILESYSTEM` | mkdir, list, delete, copy, move, exists, cwd |
| `SEARCH` | Search text/regex across files (ripgrep) |
| `GIT` | Git operations |
| `MEMORY` | Persistent key-value store |
| `DATETIME` | Current date and time |
| `WEB_SEARCH` | Search web (DuckDuckGo) |
| `READ_URL` | Fetch and read any webpage |
| `PROCESS` | System process management |

### Hotkeys (TUI mode)

| Key | Action |
|-----|--------|
| `Ctrl+C` | Exit |
| `Escape` | Stop current task |
| `Ctrl+L` | Clear chat |
| `Tab` | Toggle focus |
| `Ctrl+V` | Paste |
| `Ctrl+Shift+C` | Copy |

### Safety

- Blocked system paths (System32, Program Files)
- Blocked dangerous commands (rm -rf /, format, shutdown)
- Auto-backup before file changes
- `/restore` command to rollback
- Loop detection (same tool 3x = auto-stop)

### Testing

```bash
pip install -e ".[test]"
python -m pytest tests/ -v
```

---

## About / Об проекте

Этот проект был разработан мной — sstpr — с помощью AI-инструментов. Я программист, но для создания этого агента активно использовал AI-ассистентов на этапах проектирования архитектуры, написания кода, отладки и тестирования. Все решения по дизайну, функционалу и архитектуре принимал я. AI был инструментом, а не автором.

This project was developed by me — sstpr — with the help of AI tools. I'm a programmer, and I actively used AI assistants for architecture design, coding, debugging, and testing. All design, feature, and architecture decisions were made by me. AI was a tool, not the author.

---

MIT License ❤️
