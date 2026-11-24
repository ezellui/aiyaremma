#!/usr/bin/env bash
# One unattended session of the diarai agent. Called from cron.
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

REPO="$HOME/diarai"
LOGDIR="$HOME/logs"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(date +%F_%H%M).log"

# Do not start a new session while the previous one is still running.
exec 9>"$HOME/.diarai.lock"
flock -n 9 || { echo "previous session still running" >> "$LOG"; exit 0; }

cd "$REPO" || exit 1
git pull --ff-only -q >> "$LOG" 2>&1 || true

PROMPT="Начинается новый сеанс. Сейчас $(date '+%Y-%m-%d %H:%M %Z'). Действуй согласно CLAUDE.md."

timeout 2h claude -p "$PROMPT" \
  --permission-mode acceptEdits \
  --permission-prompts none \
  >> "$LOG" 2>&1

# Safety net: commit and push whatever the session left behind.
git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "Сеанс $(date '+%Y-%m-%d %H:%M'): несохранённое" >> "$LOG" 2>&1
fi
git push -q >> "$LOG" 2>&1 || true
