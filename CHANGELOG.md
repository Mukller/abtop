# Changelog

## [Unreleased]

### Fixed
- `__main__.py` лежал в корне репозитория, а не в пакете `abtop/`, и не было
  `[build-system]` в `pyproject.toml` — установленная через `pip install`
  команда `abtop` падала с `ModuleNotFoundError: No module named 'abtop'`
- `import curses` на верхнем уровне модуля ломал даже `--once` на Windows,
  где `curses` не входит в stdlib — импорт вынесен внутрь TUI-режима,
  `--once` теперь работает без curses
- `print()` с юникодными символами (тире, стрелки) падал с
  `UnicodeEncodeError` в Windows-консолях с кодировкой cp1251/cp866 —
  stdout принудительно переключается на UTF-8

## [0.1.0] — 2026-06-23

Первый релиз.

- Мониторинг Claude Code, Cursor, GitHub Copilot, Aider, Continue
- TUI с таблицей агентов, статусами, метриками токенов
- Примерный подсчёт стоимости по тарифам API
- Навигация клавишами
