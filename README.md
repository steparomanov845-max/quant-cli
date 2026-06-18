# QUANT CLI 3.0 ❤️

```
  ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗
 ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝
 ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   
 ██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   
 ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   
  ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝  
```

**QUANT CLI 3.0 — Your AI. Your Rules. Your Data stays with you. ❤️**

[Русский](#русский) | [English](#english)

---

## Русский

### Что это?

QUANT CLI — локальный AI-агент для работы с кодом в терминале. 100% приватность, данные остаются на твоей машине.

### Возможности

- **Стриминг** — токены появляются по мере генерации
- **4 провайдера** — LM Studio, Ollama, OpenAI, DeepSeek
- **12 инструментов** — файлы, shell, git, веб, память, процессы
- **6 режимов** — chat, agent, debug, arch, refactor, research
- **Авто-определение модели** и контекста
- **i18n** — русский и английский
- **Темы** — dark, purple, neon
- **Плагины** — добавляй свои инструменты
- **Безопасность** — блокировка опасных команд, бэкапы

### Установка

```bash
pip install quant-cli
quant
```

### Запуск

```bash
quant                          # LM Studio
quant --provider ollama        # Ollama
quant --provider openai        # OpenAI
```

### Команды

| Команда | Описание |
|---------|----------|
| `/help` | Справка |
| `/mode <имя>` | Режим работы |
| `/model [auto]` | Модели |
| `/lang ru` | Язык |
| `/theme dark` | Тема |
| `/confirm off` | Отключить подтверждения |
| `/tokens` | Токены |
| `/exit` | Выход |

### Инструменты

READ_FILE, WRITE_FILE, EDIT_FILE, CMD, FILESYSTEM, SEARCH, GIT, MEMORY, DATETIME, WEB_SEARCH, READ_URL, PROCESS

---

## English

### What is this?

QUANT CLI is a local AI coding agent for the terminal. 100% private — your data stays on your machine.

### Features

- **Streaming** — tokens appear as the model generates them
- **4 providers** — LM Studio, Ollama, OpenAI, DeepSeek
- **12 tools** — files, shell, git, web, memory, processes
- **6 modes** — chat, agent, debug, arch, refactor, research
- **Auto-detection** of model and context
- **i18n** — English and Russian
- **Themes** — dark, purple, neon
- **Plugins** — add your own tools
- **Safety** — blocks dangerous commands, auto-backup

### Install

```bash
pip install quant-cli
quant
```

### Run

```bash
quant                          # LM Studio
quant --provider ollama        # Ollama
quant --provider openai        # OpenAI
```

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Help |
| `/mode <name>` | Switch mode |
| `/model [auto]` | Models |
| `/lang en` | Language |
| `/theme dark` | Theme |
| `/confirm off` | Disable confirmations |
| `/tokens` | Token usage |
| `/exit` | Exit with summary |

### Tools

READ_FILE, WRITE_FILE, EDIT_FILE, CMD, FILESYSTEM, SEARCH, GIT, MEMORY, DATETIME, WEB_SEARCH, READ_URL, PROCESS

---

## About

Разработано sstpr с помощью AI-инструментов. Все решения по дизайну и архитектуре — мои. AI был инструментом, не автором.

Developed by sstpr using AI tools. All design and architecture decisions were mine. AI was a tool, not the author.

---

MIT License ❤️
