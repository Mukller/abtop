<div align="center">

[Русский](README.md) • **English**

</div>

# abtop

<p align="center">
  <a href="https://github.com/Mukller">
    <img src="https://img.shields.io/badge/Anton%20Petnitsky-Developer-0d1117?style=for-the-badge&logo=github&logoColor=white&labelColor=0d1117&color=58a6ff" alt="Anton Petnitsky" />
  </a>
</p>


`htop` for AI agents. See what Claude Code, Cursor, Copilot and other coding agents are doing right now: files, tokens, cost, time.

Real output of `abtop --once`, captured while writing this very README
(agent = this Claude Code session itself):

```
$ abtop --once
Agent        PID     Status     Tokens    Cost      
───────────────────────────────────────────────────────
claude       7908    active     —         —         
```

The full TUI mode (`abtop` without `--once`) refreshes live and looks like a
classic `htop`, just for AI agents instead of OS processes.

## Run

```bash
pip install abtop
abtop            # interactive TUI (refreshes every --interval)
abtop --once     # one-shot output, no TUI — works without curses

# from source
python -m abtop
```

On Windows, the interactive TUI requires `pip install windows-curses`
(stdlib `curses` only ships on Linux/macOS) — `--once` works without it.

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
