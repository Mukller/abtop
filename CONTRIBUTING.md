# Contributing

## Как помочь

Принимаю PR с:
- Поддержкой новых агентов (добавить в соответствующий модуль)
- Новыми метриками для существующих агентов
- Улучшением TUI (layout, цвета)
- Исправлением парсинга лог-файлов

## Как делать

```bash
git clone https://github.com/Mukller/abtop
cd abtop
pip install -e ".[dev]"
python -m abtop
```

## Добавление нового агента

Реализуйте интерфейс в `abtop/agents/`:

```python
class MyAgent:
    name = "myagent"
    def detect(self) -> bool: ...
    def metrics(self) -> AgentMetrics: ...
```

## Стиль

- `ruff format` и `ruff check`
- Типизация обязательна
- Каждый агент — отдельный файл в `abtop/agents/`
