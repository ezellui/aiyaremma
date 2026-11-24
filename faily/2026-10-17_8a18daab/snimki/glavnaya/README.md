# diarai: установка в Ubuntu-виртуалке

Все команды выполняются по SSH в виртуалке.

## 1. Отдельный пользователь

Агент живёт под своим пользователем. Так ваши остальные проекты в виртуалке ему недоступны, а его настройки нельзя подменить из папки.

```bash
sudo adduser diarai
sudo apt install -y git bubblewrap socat
```

Ubuntu 24 по умолчанию не даёт bubblewrap создавать пространства имён. Проверьте:

```bash
sysctl kernel.apparmor_restrict_unprivileged_userns
```

Если команда выдала `1`, добавьте профиль для bwrap:

```bash
sudo tee /etc/apparmor.d/bwrap > /dev/null <<'EOF'
abi <abi/4.0>,
include <tunables/global>

profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
  include if exists <local/bwrap>
}
EOF
sudo systemctl reload apparmor
```

Дальше всё делается от имени нового пользователя: `sudo -iu diarai`.

## 2. Claude Code и вход

```bash
curl -fsSL https://claude.ai/install.sh | bash
source ~/.bashrc
claude    # войти, как описано раньше: ссылка → браузер → код обратно в терминал
```

После входа выйдите командой `/exit`.

## 3. Доступ к репозиторию: ключ только для diarai

```bash
ssh-keygen -t ed25519 -f ~/.ssh/diarai -N "" -C diarai-vm
cat ~/.ssh/diarai.pub
```

Выведенный открытый ключ добавьте на GitHub: репозиторий diarai → Settings → Deploy keys → Add deploy key, с галочкой **Allow write access**. Такой ключ открывает ровно этот репозиторий и никакой другой.

```bash
cat >> ~/.ssh/config <<'EOF'
Host github.com
  IdentityFile ~/.ssh/diarai
  IdentitiesOnly yes
EOF
ssh -T git@github.com    # подтвердите отпечаток github.com

git clone git@github.com:USER/diarai.git ~/diarai
cd ~/diarai
git config user.name "USER"
git config user.email "sheogorath2006@gmail.com"
```

## 4. Раскладка файлов

Перенесите файлы комплекта через WinSCP, затем:

```bash
mkdir -p ~/.claude ~/bin ~/diarai/inbox
cp settings.json ~/.claude/settings.json
cp run-session.sh ~/bin/ && chmod +x ~/bin/run-session.sh
cp CLAUDE.md ~/diarai/CLAUDE.md
echo "/inbox/" >> ~/diarai/.gitignore
cd ~/diarai && git add CLAUDE.md .gitignore && git commit -m "Устав" && git push
```

Ваши материалы кладите в `~/diarai/inbox/`.

## 5. Пробный запуск вручную

```bash
tmux new -s diarai
cd ~/diarai && claude
```

Внутри сессии проверьте:

- `/context`: `CLAUDE.md` должен быть в списке Memory files;
- `/sandbox`: песочница включена, вкладки Dependencies нет.

Затем напишите «Начинается новый сеанс. Действуй согласно CLAUDE.md.» и посмотрите, как агент ведёт себя первый раз.

## 6. Расписание

```bash
crontab -e
```

Добавьте строку (здесь сеанс каждые 6 часов, в :07):

```
7 */6 * * * /home/diarai/bin/run-session.sh
```

Логи сеансов пишутся в `~/logs/`, а сделанное агентом появляется в репозитории.

## Что можно поменять

- **Материалы публиковать вместе с остальным.** Уберите `/inbox/` из `.gitignore` и соответствующую строку из CLAUDE.md.
- **Закрыть агенту веб.** Удалите блок `permissions.allow` из `settings.json`.
- **Частота и длительность сеансов.** Задаются строкой в crontab и `timeout 2h` в `run-session.sh`. Сеансы расходуют лимиты той же подписки, что и ваша обычная работа с Claude.
- **Репозиторий приватный.** Поправьте строку «Он открыт…» в CLAUDE.md.
