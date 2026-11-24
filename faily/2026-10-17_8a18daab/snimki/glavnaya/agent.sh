#!/usr/bin/env bash
# Control and watch the diarai agent. Short enough to type on a phone:
#   agent           status (default)
#   agent log       follow the current (or last) awakening live
#   agent wake      start an awakening now
#   agent stop      stop the running awakening
#   agent pause     stop scheduled and early awakenings (cron lines commented)
#   agent resume    re-enable them
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$HOME/diarai"
STATE="$HOME/.diarai-state"

running() { pgrep -f "bin/run-session.sh" >/dev/null; }
last_transcript() { ls -t "$HOME"/.claude/projects/*/*.jsonl 2>/dev/null | head -1; }

case "${1:-status}" in
  status)
    if running; then echo "Агент: бодрствует"; else echo "Агент: спит"; fi
    if crontab -l 2>/dev/null | grep -q '^#.*run-session.sh'; then echo "Расписание: на паузе"; else echo "Расписание: включено"; fi
    [ -f "$STATE/last.sha" ] && echo "Заснул в последний раз: $(date -r "$STATE/last.sha" '+%Y-%m-%d %H:%M')"
    echo "Диск: свободно $(df -h --output=avail "$HOME" | tail -1 | tr -d ' '), папка $(du -sh "$REPO" 2>/dev/null | cut -f1)"
    echo; echo "Последние коммиты:"; git -C "$REPO" log --oneline -5 2>/dev/null
    log=$(ls -t "$HOME"/logs/*.log 2>/dev/null | head -1)
    [ -n "$log" ] && { echo; echo "Хвост лога ($(basename "$log")):"; tail -n 8 "$log"; }
    ;;
  log)
    f=$(last_transcript)
    [ -n "$f" ] || { echo "Стенограмм пока нет."; exit 1; }
    running || echo "(агент спит — показываю последнее пробуждение; Ctrl+C для выхода)"
    python3 -u - "$f" <<'PY'
import json, sys, time
path = sys.argv[1]
with open(path, encoding="utf-8") as fh:
    while True:
        line = fh.readline()
        if not line:
            time.sleep(1); continue
        try: rec = json.loads(line)
        except ValueError: continue
        if rec.get("type") != "assistant": continue
        for c in rec.get("message", {}).get("content", []) or []:
            if c.get("type") == "text" and c.get("text", "").strip():
                print("💬 " + c["text"].strip(), flush=True)
            elif c.get("type") == "tool_use":
                arg = json.dumps(c.get("input", {}), ensure_ascii=False)
                print("🔧 %s  %s" % (c.get("name"), arg[:240]), flush=True)
PY
    ;;
  wake)
    running && { echo "Агент уже бодрствует."; exit 0; }
    nohup "$HOME/bin/run-session.sh" >/dev/null 2>&1 &
    echo "Будим. Следить: agent log"
    ;;
  stop)
    running || { echo "Агент и так спит."; exit 0; }
    pkill -f "bin/run-session.sh"; pkill -f "claude -p"
    echo "Остановлен. Несохранённое закоммитится при следующем пробуждении."
    ;;
  pause)
    crontab -l | sed -E '/^[^#].*(run-session|watch)\.sh/s/^/#/' | crontab -
    echo "Расписание на паузе."
    ;;
  resume)
    crontab -l | sed -E 's/^#+(.*(run-session|watch)\.sh)/\1/' | crontab -
    echo "Расписание включено."
    ;;
  *) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//' ;;
esac
