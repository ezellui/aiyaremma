import json, os
os.chdir('/home/claude/diarai-kit')

p = 'settings.json'
d = json.load(open(p))
items = list(d.items())
env = {"HTTPS_PROXY": "http://10.0.2.2:10809", "HTTP_PROXY": "http://10.0.2.2:10809",
       "NO_PROXY": "localhost,127.0.0.1"}
d = dict(items[:3] + [("env", env)] + items[3:])
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
open(p, 'a').write('\n')

p = 'run-session.sh'
s = open(p).read()
a = 'REPO="$HOME/diarai"'
assert a in s
s = s.replace(a, '''# Network exit goes through v2rayN on the host (VirtualBox NAT: host is 10.0.2.2).
# Keep in sync with "env" in ~/.claude/settings.json.
PROXY="http://10.0.2.2:10809"
export HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" NO_PROXY="localhost,127.0.0.1"

REPO="$HOME/diarai"''', 1)
a = '# What changed in the space since the end of the previous session?'
assert a in s
s = s.replace(a, '''# Without the host proxy the agent cannot reach its model: wait for it
# up to 5 minutes (v2rayN may still be starting), otherwise skip this boot.
for i in $(seq 1 30); do
  curl -s -o /dev/null --max-time 10 https://api.anthropic.com && break
  [ "$i" -eq 30 ] && { echo "proxy $PROXY unreachable, session skipped" >> "$LOG"; exit 0; }
  sleep 10
done

''' + a)
open(p, 'w').write(s)

p = 'README.md'
s = open(p).read()

def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b)

rep('''## 2. Claude Code и вход

```bash
curl -fsSL https://claude.ai/install.sh | bash''', '''## 2. Сеть через v2rayN, Claude Code и вход

Виртуалка выходит к Claude через v2rayN на хосте. В v2rayN включите «Разрешить подключения из локальной сети» и разрешите его в брандмауэре Windows для частных сетей. При NAT в VirtualBox хост виден из виртуалки как `10.0.2.2`. Порт — HTTP-порт v2rayN: в комплекте везде стоит `10809`, и если у вас другой, замените его в `settings.json`, `run-session.sh` и строках ниже.

```bash
echo 'export HTTPS_PROXY=http://10.0.2.2:10809 HTTP_PROXY=http://10.0.2.2:10809 NO_PROXY=localhost,127.0.0.1' >> ~/.bashrc
source ~/.bashrc
curl -sI https://claude.ai | head -1    # должен прийти ответ, а не таймаут

curl -fsSL https://claude.ai/install.sh | bash''')
rep('Логи сеансов пишутся в `~/logs/`, а сделанное агентом появляется в репозитории.',
    'Логи сеансов пишутся в `~/logs/`, а сделанное агентом появляется в репозитории.\n\n'
    'Пробуждению нужен запущенный на хосте v2rayN. Скрипт ждёт его до пяти минут после загрузки. '
    'Если прокси так и не ответил, пробуждение пропускается (в логе будет строка `proxy … unreachable`), '
    'а учёт изменений не сбивается: всё накопится до следующего раза.')
open(p, 'w').write(s)
print('ok')
