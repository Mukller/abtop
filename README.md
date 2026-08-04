<div align="center">

[English](README_EN.md) • **Русский**

</div>

# abtop

<p align="center">
  <a href="https://github.com/Mukller">
    <img src="https://img.shields.io/badge/Anton%20Petnitsky-Developer-0d1117?style=for-the-badge&logo=github&logoColor=white&labelColor=0d1117&color=58a6ff" alt="Anton Petnitsky" />
  </a>
</p>


`htop` для AI-агентов. Смотришь что делает Claude Code, Cursor, Copilot
и другие кодинг-агенты прямо сейчас: файлы, токены, стоимость, время.

Реальный вывод `abtop --once`, снятый прямо во время написания этого README
(agent = эта самая Claude Code сессия):

```
$ abtop --once
Агент        PID     Статус     Токены    Стоимость 
───────────────────────────────────────────────────────
claude       7908    active     —         —         
```

Полноценный TUI-режим (`abtop` без `--once`) обновляется в реальном времени и
выглядит как классический `htop`, только по AI-агентам вместо процессов ОС.

## Запуск

```bash
pip install abtop
abtop            # интерактивный TUI (обновляется по --interval)
abtop --once     # разовый вывод без TUI — работает без curses

# или из исходников
python -m abtop
```

На Windows интерактивный TUI-режим требует `pip install windows-curses`
(в stdlib `curses` есть только на Linux/macOS) — `--once` работает без него.

## Что отслеживает

| Метрика | Источник |
|---------|----------|
| Активные процессы агентов | `/proc` / `psutil` |
| Количество открытых файлов | lsof / psutil |
| Использование токенов | лог-файлы агентов |
| Примерная стоимость | по тарифам API |
| Время работы сессии | uptime процесса |

## Поддерживаемые агенты

- **Claude Code** (`claude` CLI)
- **Cursor** (читает `.cursor/logs/`)
- **GitHub Copilot** (читает VSCode extension logs)
- **Aider** (парсит `aider.log`)
- **Continue** (читает `.continue/logs/`)
