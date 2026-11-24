#!/usr/bin/env bash
# Wake the agent early when its space changes from outside: new commits on
# GitHub or edited files in the folder (inbox/ included). Cron: every 5 min.
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

REPO="$HOME/diarai"
STATE="$HOME/.diarai-state"
GAP_MIN=10   # minimum pause after the previous awakening, in minutes

# Not before the first awakening has finished.
[ -f "$STATE/last.sha" ] || exit 0
# Not while an awakening is running.
flock -n "$STATE/lock" true || exit 0
# Not sooner than GAP_MIN after the last awakening ended (or was attempted).
now=$(date +%s)
for f in "$STATE/last.sha" "$STATE/last-wake"; do
  [ -f "$f" ] && [ $(( now - $(stat -c %Y "$f") )) -lt $(( GAP_MIN * 60 )) ] && exit 0
done

# Same procedure as in run-session.sh.
snapshot() {
  ( cd "$REPO" && find . \( -path ./.git -o -path ./ext -o -name node_modules \
      -o -name .venv -o -name venv -o -name __pycache__ \) -prune \
      -o -type f -print0 | sort -z | xargs -0 -r sha256sum ) > "$1"
}

cd "$REPO" || exit 1
reason=""

# 1. New commits on GitHub that are not here yet.
if timeout 60 git fetch -q 2>/dev/null; then
  behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)
  [ "$behind" -gt 0 ] && reason="github"
fi

# 2. Files changed in the folder since the agent fell asleep. Wake only when
#    the folder has stayed the same for one check interval, so that a batch
#    of edits in progress is not caught half-done.
snapshot "$STATE/watch.sha"
if ! cmp -s "$STATE/watch.sha" "$STATE/last.sha"; then
  if cmp -s "$STATE/watch.sha" "$STATE/pending.sha" 2>/dev/null; then
    reason="${reason:+$reason+}folder"
  else
    cp "$STATE/watch.sha" "$STATE/pending.sha"
  fi
fi

[ -n "$reason" ] || exit 0
rm -f "$STATE/pending.sha"
touch "$STATE/last-wake"
exec "$HOME/bin/run-session.sh" "$reason"
