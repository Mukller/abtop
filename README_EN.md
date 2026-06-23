# abtop

`htop` for AI agents. See what Claude Code, Cursor, Copilot and other coding agents are doing right now: files, tokens, cost, time.

## Usage

```bash
pip install abtop
abtop

# or from source
python -m abtop
```

## What it tracks

| Metric | Source |
|--------|--------|
| Active agent processes | `/proc` / `psutil` |
| Open file count | lsof / psutil |
| Token usage | agent log files |
| Estimated cost | API pricing |
| Session uptime | process uptime |

## Supported agents

- **Claude Code** (`claude` CLI)
- **Cursor** (reads `.cursor/logs/`)
- **GitHub Copilot** (reads VSCode extension logs)
- **Aider** (parses `aider.log`)
- **Continue** (reads `.continue/logs/`)
