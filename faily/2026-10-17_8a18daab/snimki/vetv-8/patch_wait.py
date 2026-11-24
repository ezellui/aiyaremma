import json, os, re
os.chdir('/home/claude/diarai-kit')

# --- run-session.sh: continuation loop with waiting -------------------------
p = 'run-session.sh'
s = open(p).read()
start = s.index('# One awakening = up to 2 hours.')
end = s.index('done\n', s.index('for round in')) + len('done\n')
new_block = r'''# One awakening = up to 2 hours, one conversation. When the agent stops early
# it is woken again in the same conversation and told how much time is left.
# Its answer may end with:
#   ЗАСЫПАЮ   - end the awakening now;
#   ЖДУ N     - pause for N minutes, then continue (sooner if the space
#               changes from outside meanwhile).
# A turn shorter than 3 minutes with neither line gets a 10-minute pause,
# so the agent is not re-woken every few seconds.
SID=$(cat /proc/sys/kernel/random/uuid)
DEADLINE=$(( $(date +%s) + 7200 ))
FLAGS=(--system-prompt-file "$SYSTEM_PROMPT" --permission-mode acceptEdits
       --permission-prompts none --strict-mcp-config)

run_turn() {  # $1 = prompt, rest = extra flags; prints the agent's answer
  local left=$(( DEADLINE - $(date +%s) ))
  timeout "$left" claude -p "$1" "${@:2}" "${FLAGS[@]}" 2>>"$LOG"
}

# Pause up to $1 minutes; return 0 early if the space changed from outside.
pause_for() {
  local until=$(( $(date +%s) + $1 * 60 ))
  [ "$until" -gt "$DEADLINE" ] && until=$DEADLINE
  snapshot "$STATE/wait.sha"
  while [ "$(date +%s)" -lt "$until" ]; do
    sleep 60
    if timeout 30 git fetch -q 2>/dev/null &&
       [ "$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)" -gt 0 ]; then
      git pull -q --rebase --autostash >> "$LOG" 2>&1
      return 0
    fi
    snapshot "$STATE/wait2.sha"
    cmp -s "$STATE/wait.sha" "$STATE/wait2.sha" || return 0
  done
  return 1
}

T0=$(date +%s)
OUT=$(run_turn "$PROMPT" --session-id "$SID")
printf '%s\n' "$OUT" >> "$LOG"
for round in $(seq 1 30); do
  printf '%s\n' "$OUT" | grep -qx '[[:space:]]*ЗАСЫПАЮ[[:space:]]*' && break
  WAIT=$(printf '%s\n' "$OUT" | grep -oE '^[[:space:]]*ЖДУ[[:space:]]+[0-9]+' | tail -1 | grep -oE '[0-9]+')
  [ -z "$WAIT" ] && [ $(( $(date +%s) - T0 )) -lt 180 ] && WAIT=10
  NOTE=""
  if [ -n "$WAIT" ]; then
    echo "--- пауза до $WAIT мин ---" >> "$LOG"
    WAIT_START=$(date +%s)
    if pause_for "$WAIT"; then
      snapshot "$STATE/wait2.sha"
      NOTE="Пауза прервана через $(( ($(date +%s) - WAIT_START) / 60 )) мин: пространство изменилось не по твоей воле:
$(compare "$STATE/wait.sha" "$STATE/wait2.sha" | head -40)
"
    else
      NOTE="Прошло $(( ($(date +%s) - WAIT_START) / 60 )) мин паузы; извне ничего не изменилось.
"
    fi
  fi
  LEFT_MIN=$(( (DEADLINE - $(date +%s)) / 60 ))
  [ "$LEFT_MIN" -lt 10 ] && break
  echo "--- продолжение $round, осталось $LEFT_MIN мин ---" >> "$LOG"
  T0=$(date +%s)
  OUT=$(run_turn "${NOTE}Пробуждение продолжается: до его конца около $LEFT_MIN мин. Посмотри, что ещё хочешь сделать: продолжи начатое, возьмись за задуманное, углубись или проверь сделанное. Если хочешь подождать (например, ответа), закончи ответ строкой «ЖДУ N» — N минут. Если сознательно решил закончить, запиши в дневнике почему и закончи ответ строкой ЗАСЫПАЮ." --resume "$SID") || break
  printf '%s\n' "$OUT" >> "$LOG"
done
'''
s = s[:start] + new_block + s[end:]
open(p, 'w').write(s)

# --- CLAUDE.md: mention waiting -------------------------------------------
p = 'CLAUDE.md'
s = open(p).read()
a = 'Если ты остановишься, а время ещё есть, тебя разбудят снова в том же пробуждении и скажут, сколько осталось.'
assert a in s
s = s.replace(a, a + ' Если хочешь подождать (ответа, изменений, просто времени), закончи ответ строкой `ЖДУ N`: тебя разбудят через N минут, а если пространство тем временем изменится не по твоей воле — раньше, и скажут, что изменилось. Так же можно ждать и посреди дела.')
open(p, 'w').write(s)

# --- settings.json: allow all Bash (still confined by the sandbox) ---------
p = 'settings.json'
d = json.load(open(p))
allow = d['permissions']['allow']
if 'Bash' not in allow:
    allow.insert(0, 'Bash')
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
open(p, 'a').write('\n')

# --- README: gitignore for sandbox placeholders, notes --------------------
p = 'README.md'
s = open(p).read()
old = 'printf "/inbox/\\n/ext/\\nnode_modules/\\n.venv/\\nvenv/\\n__pycache__/\\n*.pyc\\n" >> ~/diarai/.gitignore'
assert old in s, 'gitignore line'
s = s.replace(old, '''cat >> ~/diarai/.gitignore <<'EOF'
/inbox/
/ext/
node_modules/
.venv/
venv/
__pycache__/
*.pyc
# пустые заглушки, которые песочница оставляет, если сеанс оборвался
/.bashrc
/.bash_profile
/.profile
/.zshrc
/.zprofile
/.gitconfig
/.gitmodules
/.ripgreprc
/.mcp.json
/.idea
/.vscode
/.claude/
EOF''')
a = '- **Сколько агент делает за пробуждение.**'
i = s.index(a); j = s.index('\n', i)
s = s[:i] + '''- **Сколько агент делает за пробуждение.** Пробуждение — одна беседа до двух часов. Если агент остановился раньше, скрипт будит его снова в той же беседе и сообщает, сколько осталось. Агент может закончить ответ строкой `ЗАСЫПАЮ` (конец пробуждения, причина — в дневнике) или `ЖДУ N` (пауза на N минут; прерывается раньше, если вы что-то запушили или поменяли в папке, и агенту сообщают, что именно). Ход короче трёх минут без этих строк получает паузу в 10 минут, чтобы агента не будили каждые несколько секунд. В логе отмечены строки `--- пауза ---` и `--- продолжение N ---`.
- **Команды оболочки.** Правило `"Bash"` в `permissions.allow` разрешает агенту любые команды без одобрения: иначе отклоняются команды с `=`, `for`, `&&`, `2>&1` и подобные, а спросить некого. Границы ставит песочница: писать можно только в своей папке, а выйти из песочницы нельзя (`allowUnsandboxedCommands: false`).''' + s[j:]
open(p, 'w').write(s)
print('ok')
