"""
abtop — мониторинг AI-агентов в терминале.

Запуск:  python -m abtop
         python -m abtop --interval 2
"""

from __future__ import annotations

import argparse
import curses
import glob
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# ──────────────────────────────────────────────
# Детекторы агентов
# ──────────────────────────────────────────────

@dataclass
class AgentInfo:
    name: str
    pid: Optional[int]
    status: str          # "active" | "idle" | "offline"
    open_files: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    uptime_s: int
    current_file: str

    @property
    def total_tokens(self) -> int:
        return self.tokens_in + self.tokens_out


def _find_procs(names: list[str]) -> list:
    """Найти процессы по имени (требует psutil)."""
    if not HAS_PSUTIL:
        return []
    result = []
    for proc in psutil.process_iter(["name", "pid", "create_time", "open_files"]):
        try:
            pname = proc.info["name"].lower()
            if any(n in pname for n in names):
                result.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return result


def _parse_claude_logs() -> tuple[int, int]:
    """Парсим ~/.claude/logs/*.jsonl для подсчёта токенов."""
    tokens_in = tokens_out = 0
    log_dir = Path.home() / ".claude" / "logs"
    if not log_dir.exists():
        return 0, 0
    for f in sorted(log_dir.glob("*.jsonl"))[-3:]:
        try:
            for line in f.read_text(errors="ignore").splitlines()[-200:]:
                try:
                    obj = json.loads(line)
                    usage = obj.get("usage", {})
                    tokens_in  += usage.get("input_tokens", 0)
                    tokens_out += usage.get("output_tokens", 0)
                except json.JSONDecodeError:
                    pass
        except OSError:
            pass
    return tokens_in, tokens_out


def _parse_aider_log() -> tuple[int, int]:
    log = Path(".aider.log")
    if not log.exists():
        log = Path.home() / ".aider.log"
    if not log.exists():
        return 0, 0
    text = log.read_text(errors="ignore")
    # ищем строки вида "Tokens: 1234 sent, 567 received"
    tin = sum(int(m) for m in re.findall(r"(\d+) sent", text))
    tout = sum(int(m) for m in re.findall(r"(\d+) received", text))
    return tin, tout


# Цены за 1M токенов (input / output), USD
PRICES: dict[str, tuple[float, float]] = {
    "claude":  (3.0,  15.0),
    "cursor":  (2.0,  10.0),
    "copilot": (0.0,   0.0),   # подписка
    "aider":   (3.0,  15.0),
    "continue":(3.0,  15.0),
}

def cost(name: str, tin: int, tout: int) -> float:
    pi, po = PRICES.get(name, (3.0, 15.0))
    return tin / 1_000_000 * pi + tout / 1_000_000 * po


# ──────────────────────────────────────────────
# Сбор данных
# ──────────────────────────────────────────────

def collect() -> list[AgentInfo]:
    agents: list[AgentInfo] = []

    # ── Claude Code ──────────────────────────
    procs = _find_procs(["claude"])
    tin, tout = _parse_claude_logs()
    if procs:
        p = procs[0]
        try:
            of = len(p.open_files()) if HAS_PSUTIL else 0
            uptime = int(time.time() - p.create_time())
            cur_file = ""
            if HAS_PSUTIL:
                try:
                    files = [f.path for f in p.open_files()
                             if not f.path.startswith("/proc")]
                    cur_file = Path(files[-1]).name if files else ""
                except psutil.AccessDenied:
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            of, uptime, cur_file = 0, 0, ""
        agents.append(AgentInfo("claude", p.pid, "active",
                                of, tin, tout, cost("claude", tin, tout),
                                uptime, cur_file))
    elif tin or tout:
        agents.append(AgentInfo("claude", None, "idle",
                                0, tin, tout, cost("claude", tin, tout), 0, ""))

    # ── Aider ────────────────────────────────
    procs = _find_procs(["aider"])
    atin, atout = _parse_aider_log()
    if procs or atin:
        p = procs[0] if procs else None
        uptime = int(time.time() - p.create_time()) if p else 0
        agents.append(AgentInfo("aider", p.pid if p else None,
                                "active" if p else "idle",
                                0, atin, atout, cost("aider", atin, atout), uptime, ""))

    # ── Cursor ───────────────────────────────
    procs = _find_procs(["cursor"])
    if procs:
        p = procs[0]
        try:
            uptime = int(time.time() - p.create_time())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            uptime = 0
        agents.append(AgentInfo("cursor", p.pid, "active",
                                0, 0, 0, 0.0, uptime, ""))

    # ── Copilot (VSCode) ─────────────────────
    procs = _find_procs(["code"])
    if procs:
        agents.append(AgentInfo("copilot", procs[0].pid, "idle",
                                0, 0, 0, 0.0, 0, ""))

    if not agents:
        agents.append(AgentInfo("(нет агентов)", None, "offline",
                                0, 0, 0, 0.0, 0, "—"))

    return agents


# ──────────────────────────────────────────────
# TUI
# ──────────────────────────────────────────────

def fmt_tokens(n: int) -> str:
    if n == 0:   return "—"
    if n < 1000: return str(n)
    return f"{n/1000:.1f}k"

def fmt_cost(c: float) -> str:
    if c == 0: return "—"
    return f"${c:.3f}"

def fmt_uptime(s: int) -> str:
    if s == 0: return "—"
    h, m = divmod(s // 60, 60)
    return f"{h:02d}:{m:02d}" if h else f"{m}м"

STATUS_COLOR = {"active": 2, "idle": 3, "offline": 1}

def draw(stdscr, agents: list[AgentInfo]) -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED,    -1)
    curses.init_pair(2, curses.COLOR_GREEN,  -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_CYAN,   -1)
    curses.init_pair(5, curses.COLOR_WHITE,  -1)
    curses.curs_set(0)
    stdscr.clear()

    h, w = stdscr.getmaxyx()
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # Заголовок
    title = f" abtop v0.1  —  AI Agent Monitor "
    stdscr.addstr(0, 0, title, curses.color_pair(4) | curses.A_BOLD)
    stdscr.addstr(0, w - len(now) - 1, now, curses.color_pair(5))

    # Колонки
    cols = [("Агент", 12), ("PID", 7), ("Статус", 10),
            ("Файлов", 7), ("Токены", 9), ("Стоимость", 10),
            ("Uptime", 8), ("Файл", 20)]

    y = 2
    x = 0
    for label, width in cols:
        stdscr.addstr(y, x, label.ljust(width), curses.A_UNDERLINE)
        x += width
    y += 1

    for ag in agents:
        if y >= h - 2: break
        x = 0
        color = curses.color_pair(STATUS_COLOR.get(ag.status, 5))

        def col(text: str, width: int, attr=0) -> None:
            nonlocal x
            s = str(text)[:width-1].ljust(width)
            stdscr.addstr(y, x, s, attr)
            x += width

        col(ag.name, 12, curses.A_BOLD)
        col(str(ag.pid) if ag.pid else "—", 7)
        status_sym = {"active": "● ", "idle": "○ ", "offline": "✗ "}.get(ag.status, "  ")
        col(status_sym + ag.status, 10, color)
        col(str(ag.open_files) if ag.open_files else "—", 7)
        col(fmt_tokens(ag.total_tokens), 9)
        col(fmt_cost(ag.cost_usd), 10)
        col(fmt_uptime(ag.uptime_s), 8)
        col(ag.current_file or "—", 20)
        y += 1

    # Подсказка
    stdscr.addstr(h-1, 0, " [q] выйти  [r] сбросить  [s] сортировать ",
                  curses.color_pair(5))


def run_tui(interval: float) -> None:
    def _main(stdscr) -> None:
        stdscr.timeout(int(interval * 1000))
        agents = collect()
        sort_key = "name"

        while True:
            draw(stdscr, agents)
            key = stdscr.getch()
            if key == ord('q'):
                break
            if key == ord('r'):
                agents = collect()
            if key == ord('s'):
                sort_key = "tokens" if sort_key == "name" else "name"
            # обновляем по таймеру
            if key == -1:
                agents = collect()
            if sort_key == "tokens":
                agents.sort(key=lambda a: a.total_tokens, reverse=True)

    curses.wrapper(_main)


# ──────────────────────────────────────────────
# main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Мониторинг AI-агентов")
    parser.add_argument("--interval", type=float, default=3.0,
                        help="секунд между обновлениями")
    parser.add_argument("--once", action="store_true",
                        help="вывести один раз и выйти")
    args = parser.parse_args()

    if not HAS_PSUTIL:
        print("psutil не установлен. Часть данных будет недоступна.")
        print("pip install psutil")

    if args.once:
        agents = collect()
        print(f"{'Агент':12} {'PID':7} {'Статус':10} {'Токены':9} {'Стоимость':10}")
        print("─" * 55)
        for ag in agents:
            print(f"{ag.name:12} {str(ag.pid or '—'):7} {ag.status:10} "
                  f"{fmt_tokens(ag.total_tokens):9} {fmt_cost(ag.cost_usd):10}")
        return

    run_tui(args.interval)


if __name__ == "__main__":
    main()
