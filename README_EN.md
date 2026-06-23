<div align="center">

[Русский](README.md) • **English**

</div>

# abtop

`htop` for AI agents. See what Claude Code, Cursor, Copilot and other coding agents are doing right now: files, tokens, cost, time.

```
╔══════════════════════════════════════════════════════╗
║ abtop v0.1  —  AI Agent Monitor          23.06.2026 ║
╠═══════════╦═══════════╦════════╦═══════╦════════════╣
║ Agent     ║ Status    ║ Files  ║ Tokens║ Cost       ║
╠═══════════╬═══════════╬════════╬═══════╬════════════╣
║ claude    ║ ● active  ║   14   ║  42k  ║  $0.63     ║
║ cursor    ║ ● active  ║    3   ║  12k  ║  $0.08     ║
║ copilot   ║ ○ idle    ║    0   ║   —   ║  —         ║
╚═══════════╩═══════════╩════════╩═══════╩════════════╝
[q] quit  [r] reset  [s] sort
```

## Run

```bash
pip install abtop
abtop

# from source
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
