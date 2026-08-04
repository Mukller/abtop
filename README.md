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

```
╔══════════════════════════════════════════════════════╗
║ abtop v0.1  —  AI Agent Monitor          23.06.2026 ║
╠═══════════╦═══════════╦════════╦═══════╦════════════╣
║ Агент     ║ Статус    ║ Файлов ║ Токен ║ Стоимость  ║
╠═══════════╬═══════════╬════════╬═══════╬════════════╣
║ claude    ║ ● active  ║   14   ║  42k  ║  $0.63     ║
║ cursor    ║ ● active  ║    3   ║  12k  ║  $0.08     ║
║ copilot   ║ ○ idle    ║    0   ║   —   ║  —         ║
╚═══════════╩═══════════╩════════╩═══════╩════════════╝
[q] выйти  [r] сбросить  [s] сортировать
```

## Запуск

```bash
pip install abtop
abtop

# или из исходников
python -m abtop
```

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
