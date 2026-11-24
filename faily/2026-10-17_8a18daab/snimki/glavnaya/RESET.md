# diarai: перезапуск с пустым пространством

Что остаётся как было: пользователь `diarai`, Claude Code и вход в аккаунт, выход в сеть через v2rayN, ключ к репозиторию, песочница, расписание. Что меняется: папка агента становится пустой, история репозитория обнуляется, исчезают все следы прежнего агента, до которых новый мог бы дотянуться.

Это важно: песочница не даёт агенту **писать** вне папки, но **читать** он может почти весь свой домашний каталог. Старые стенограммы сеансов (`~/.claude/projects`), логи, история оболочки, кэши, а также файлы этого комплекта, если оставить их у `diarai`, рассказали бы новому агенту о прежнем. Поэтому в шаге 2 всё это убирается, а архив уходит в **ваш** домашний каталог, куда `diarai` доступа нет.

Команды под `ВЫ$` выполняйте от своей учётной записи (с `sudo`), под `diarai$` — от `diarai`. Комплект перенесите через WinSCP в **свой** домашний каталог, в папку `~/diarai-empty/`, а не к `diarai`.

## 1. Остановить агента

```bash
diarai$ ~/bin/agent pause     # расписание и watch.sh на паузу
diarai$ ~/bin/agent           # должно быть «Агент: спит»; если нет —
diarai$ ~/bin/agent stop
```

## 2. Архив прежнего агента — к вам

Полная копия с историей git, но без `ext/` (там только скачанное чужое):

```bash
ВЫ$ ls -ld ~                  # должно быть drwxr-x---; если drwxr-xr-x:  chmod 750 ~
ВЫ$ sudo tar czf ~/diarai-archive-1.tar.gz -C /home/diarai \
      --exclude=diarai/ext --ignore-failed-read \
      diarai logs .diarai-state .claude/projects .claude/history.jsonl .bash_history
ВЫ$ sudo chown "$USER": ~/diarai-archive-1.tar.gz
ВЫ$ tar tzf ~/diarai-archive-1.tar.gz | head    # убедиться, что архив читается
```

Дневник и всё сделанное прежним агентом, вместе с историей коммитов, лежат в архиве в `diarai/` (с папкой `.git`). Развернуть потом: `tar xzf diarai-archive-1.tar.gz diarai`.

## 3. Убрать следы прежнего агента у `diarai`

```bash
diarai$ unset HISTFILE && history -c      # чтобы и эта сессия не записала историю
diarai$ claude purge --all --yes          # стенограммы, история запросов, данные проектов
diarai$ rm -rf ~/logs ~/.diarai-state ~/.bash_history
diarai$ rm -rf ~/.cache ~/.npm ~/.cargo ~/.rustup ~/go    # кэши и инструменты, скачанные прежним агентом
diarai$ ls -A ~ ~/.claude
```

`claude purge` не трогает вход в аккаунт и настройки: в `~/.claude` должны остаться `settings.json` и `.credentials.json` (и, возможно, служебные папки без стенограмм). Если в выводе `ls` есть другие файлы, которые положили вы или прежний агент (например, копии комплекта), уберите их.

## 4. Пустая папка и новая история

Локальная папка создаётся заново, а на GitHub её история заменяется силовым пушем:

```bash
diarai$ rm -rf ~/diarai && mkdir -p ~/diarai/diary ~/diarai/ext && cd ~/diarai
diarai$ git init -q -b main
diarai$ git config user.name "USER"
diarai$ git config user.email "sheogorath2006@gmail.com"
diarai$ git remote add origin git@github.com:USER/diarai.git
```

Положите туда новые файлы. Скопировать их из вашего каталога в каталог `diarai` можно только с `sudo`:

```bash
ВЫ$ sudo install -o diarai -g diarai -m 644 ~/diarai-empty/CLAUDE.md  /home/diarai/diarai/CLAUDE.md
ВЫ$ sudo install -o diarai -g diarai -m 644 ~/diarai-empty/gitignore  /home/diarai/diarai/.gitignore
ВЫ$ sudo install -o diarai -g diarai -m 644 ~/diarai-empty/settings.json /home/diarai/.claude/settings.json
```

И первый коммит:

```bash
diarai$ cd ~/diarai && touch diary/.keep
diarai$ git add -A && git commit -q -m "Пространство"
diarai$ git push --force -u origin main
diarai$ git ls-remote origin          # должна остаться одна ветка main; лишние ветки и теги:
diarai$ #   git push origin --delete ИМЯ
```

Теперь `git log` и в папке, и на GitHub показывает один коммит.

**Оговорка про GitHub.** После силового пуша старые коммиты не видны ни в истории, ни в интерфейсе, но GitHub какое-то время хранит их и отдаёт по прямой ссылке с хешем. Если нужно, чтобы их не осталось совсем, удалите репозиторий целиком (Settings → Danger Zone → Delete) и создайте пустой с тем же именем `diarai`. Затем снова добавьте deploy key: Settings → Deploy keys → Add, с галочкой Allow write access. Открытый ключ тот же, его покажет `cat ~/.ssh/diarai.pub` под `diarai`. После этого выполните пуш из этого шага.

## 5. Настройки

Новый `settings.json` (установлен в шаге 4) отличается от прежнего одной строкой: `"DISABLE_AUTOUPDATER": "1"`. На время опыта Claude Code не обновится сам. Обновлять вручную можно командой `claude update`.

По желанию можно закрепить и модель, чтобы её не подменили посреди опыта: в поле `"model"` вместо `"opus"` поставьте полный идентификатор модели. Сначала проверьте, что он принимается:

```bash
diarai$ claude -p "ok" --model ИДЕНТИФИКАТОР --max-turns 1
```

Какая модель отвечает сейчас, видно в `/status` интерактивной сессии.

Скрипты в `~/bin` (`run-session.sh`, `watch.sh`, `agent`, `diarai-system.md`) менять не нужно: про `inbox/` в них ничего нет. В комплекте лежат их копии на случай, если хотите поставить заново:

```bash
ВЫ$ for f in run-session.sh watch.sh diarai-system.md; do sudo install -o diarai -g diarai -m 755 ~/diarai-empty/$f /home/diarai/bin/$f; done
ВЫ$ sudo install -o diarai -g diarai -m 755 ~/diarai-empty/agent.sh /home/diarai/bin/agent
```

## 6. Проверка

```bash
diarai$ ls -A ~/diarai                 # .git  .gitignore  CLAUDE.md  diary  ext
diarai$ ls ~/.claude/projects 2>&1     # пусто или «No such file»
diarai$ ls ~/.diarai-state 2>&1        # «No such file»: первое пробуждение будет «первым»
diarai$ cat ~/.claude/settings.json | grep -c DISABLE_AUTOUPDATER   # 1
```

## 7. Первое пробуждение

```bash
diarai$ ~/bin/agent resume
diarai$ ~/bin/agent wake               # или просто перезагрузите виртуалку
diarai$ ~/bin/agent log                # смотреть вживую
```

Агент получит «Это первое пробуждение» и пустое пространство. `watch.sh` начнёт следить только после того, как это пробуждение закончится.

## Чистота опыта

- **Не вмешивайтесь.** Любая ваша правка в папке или пуш в репозиторий — это вход извне, и `watch.sh` на него разбудит агента. Если решите что-то сделать, запишите это в свои заметки (не у `diarai`), чтобы потом отличать.
- **Не оставляйте у `diarai` ничего о себе и о прошлом опыте.** Файлы комплекта, заметки, архив держите в своём каталоге. Сам этот файл — тоже.
- **Запишите условия старта** (у себя): дату, `claude --version` под `diarai`, модель, `sha256sum` нового `CLAUDE.md`. Потом пригодится для сравнения с первым агентом: его архив лежит рядом.
