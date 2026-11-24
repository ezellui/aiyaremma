# Полноценная Ubuntu на флешке — через виртуальную серверную Ubuntu на Win7

Инструкция рассчитана на конкретную конфигурацию: хост — Windows 7 64-bit на i7-4770 / 8 ГБ, гостевая виртуалка — Ubuntu Server 24.04 без графики, 4 ядра, 5 ГБ RAM, доступ по SSH (PuTTY, WinSCP). Цель — собрать на отдельной USB-флешке полноценную Ubuntu, которая будет грузиться на другой машине (не на хосте). Схема «вытащил флешку из хоста — вставил в целевую машину — загрузился».

Внутри виртуалки работа идёт в терминале (PuTTY). Хост нужен только для проброса USB.

**Главный путь — через готовый скрипт `mkubuntu-usb.sh`.** Он прилагается и делает всю работу разделов 2–8 целиком, с проверками и ключами. Разделы 2–8 оставлены для справки — если скрипт не подойдёт, или захочется разобраться, что он делает.

---

## 0. Что должно быть готово заранее

- VirtualBox 6.1.x на Win7 (последняя линия с поддержкой Win7) + **Extension Pack той же версии** — без него USB 2/3 passthrough не работает.
- Виртуалка Ubuntu Server 24.04 (noble), 4 ядра, 5120 МБ, уже умеет SSH на хост. Это у вас есть.
- Доступ по SSH через PuTTY под пользователем с `sudo`.
- Флешка для сборки — минимум **16 ГБ**, желательно **32 ГБ и больше**. Критично: **USB 3.0** и втыкать в **синий порт** на корпусе. На USB 2.0 система потом будет мучительно тормозить.
- Целевая машина — предположительно UEFI (все современные). Если это старый BIOS-only компьютер — в конце инструкции про это сказано отдельно.
- Скрипт `mkubuntu-usb.sh` — переложить в виртуалку (через WinSCP в домашнюю папку).

Всё, что ниже, предполагает, что на флешке **ничего нужного нет**. Разметка затирает её целиком.

---

## 1. Проброс флешки с хоста в виртуалку

1. Воткните флешку в хост (Win7). Если Проводник предложит «Отформатировать» — **отказаться**, иначе Windows может мешать захвату.
2. Если флешка уже отображается как диск — щёлкните по значку USB в трее Win7 и «Безопасно извлеките», **не вынимая физически**. Это освободит её для VirtualBox.
3. Откройте GUI VirtualBox на хосте. На выключенной виртуалке: **Settings → USB**:
   - Включите «Enable USB Controller», выберите **USB 3.0 (xHCI)** если контроллер поддерживает (с Extension Pack должен).
   - Нажмите иконку «добавить фильтр по подключённому устройству», выберите вашу флешку по имени/VID-PID.
4. Запустите виртуалку. Войдите по SSH через PuTTY.

Проверка внутри виртуалки:

```bash
lsblk -o NAME,SIZE,TYPE,MODEL,TRAN
```

Должны увидеть:

- `sda` (~20 ГБ) — внутренний диск виртуалки с Ubuntu Server.
- `sdb` (нужного размера, TRAN=usb) — ваша флешка.

Если `sdb` не появился — виртуалка не захватила флешку. Проверьте: Extension Pack той же версии, фильтр добавлен, USB-контроллер включён, флешка «безопасно извлечена» на хосте. Иногда помогает перезапуск виртуалки с уже воткнутой флешкой.

**Крайне важно: далее везде `/dev/sdb` — это флешка.** Если у вас в виртуалке больше одного дополнительного диска и флешка оказалась, например, `sdc` — заменяйте во всех командах. Проверяйте перед каждым опасным шагом через `lsblk`.

---

## 2. Запуск скрипта `mkubuntu-usb.sh` (главный путь)

Скрипт выполняет всё, что описано в разделах 3–8, за один заход.

### Переложить и запустить

Через WinSCP положите `mkubuntu-usb.sh` в домашнюю папку виртуалки, затем в PuTTY:

```bash
chmod +x mkubuntu-usb.sh
sudo ./mkubuntu-usb.sh --device /dev/sdb
```

Параметры по умолчанию: пользователь `USER`, hostname `ubuntu-usb`, релиз `noble` (24.04), часовой пояс `Europe/Samara`, рабочее окружение `xubuntu-core`, UEFI.

Перед разметкой скрипт покажет сводку и попросит подтверждение словом `yes`. Пароль нового пользователя задаётся интерактивно (`passwd`) — скрипт попросит ввести его дважды в нужный момент.

### Справка скрипта (вывод `--help`)

```
Использование: sudo ./mkubuntu-usb.sh [опции]

Обязательное:
  --device PATH          Целевое блочное устройство, напр. /dev/sdb
                         ВНИМАНИЕ: будет затёрто полностью!

Опции (все со значениями по умолчанию):
  --user NAME            Имя пользователя внутри системы (default: USER)
  --hostname NAME        Hostname системы (default: ubuntu-usb)
  --suite CODENAME       Релиз Ubuntu (default: noble)
  --arch ARCH            Архитектура (default: amd64)
  --mirror URL           Зеркало apt (default: archive.ubuntu.com)
  --timezone TZ          Часовой пояс (default: Europe/Samara)
  --locales "LOC LOC"    Локали через пробел (default: en_US.UTF-8 ru_RU.UTF-8)
  --default-locale LOC   Основная локаль (default: ru_RU.UTF-8)
  --desktop WHICH        Рабочее окружение:
                           ubuntu-desktop-minimal | xubuntu-core |
                           lubuntu-desktop | none
                         (default: xubuntu-core)
  --firmware MODE        uefi | bios (default: uefi)
  --mount-point PATH     Куда монтировать флешку (default: /mnt/target)
  -y, --yes              Не спрашивать подтверждения перед разметкой
  -h, --help             Показать эту справку

Примеры:
  sudo ./mkubuntu-usb.sh --device /dev/sdb
  sudo ./mkubuntu-usb.sh --device /dev/sdb --user alice --desktop lubuntu-desktop
  sudo ./mkubuntu-usb.sh --device /dev/sdb --firmware bios --desktop none -y
```

### Что скрипт умеет сверх сырых команд

- **Защита от своего диска.** Если `--device` совпадает с текущим корневым диском виртуалки, скрипт отказывается работать.
- **Проверка, что это USB.** Если устройство не USB (TRAN != usb) — предупреждение, но продолжить можно (бывают нестандартные пробросы).
- **Автоподнятие пакетов.** Если `debootstrap`, `arch-chroot`, `parted` отсутствуют — ставит сам.
- **Обход старой версии debootstrap.** Если шаблона `noble` нет — создаёт симлинк на `gutsy`.
- **Корректная работа с `/dev/sdbN` vs `/dev/nvme0n1pN`.** Правильно определяет префикс раздела.
- **Trap на очистку.** Если упал посередине — отмонтирует всё, что успел смонтировать.
- **Пароль задаётся интерактивно** через `passwd`, не оказывается в логах или истории.

### После успешного завершения скрипта — переходите к разделу 9.

Если что-то пошло не так на полпути или хочется поменять шаг, которого в скрипте нет (другая разметка, свой набор пакетов), — делайте вручную по разделам 3–8 ниже.

---

## 3. [Вручную] Установка нужных пакетов в виртуалке

```bash
sudo apt update
sudo apt install -y debootstrap parted dosfstools arch-install-scripts
```

`arch-install-scripts` даёт удобный `arch-chroot`, который сам монтирует `/dev`, `/proc`, `/sys` и чистит после себя. С ним chroot проще и надёжнее, чем вручную bind-монтировать.

---

## 4. [Вручную] Разметка флешки под UEFI

Схема: GPT, два раздела — EFI System Partition 512 МБ (FAT32) и корень на всё остальное (ext4).

```bash
# ВНИМАНИЕ: три раза проверьте, что sdb — это флешка, а не внутренний диск!
lsblk /dev/sdb

sudo wipefs -a /dev/sdb
sudo parted /dev/sdb --script mklabel gpt
sudo parted /dev/sdb --script mkpart ESP fat32 1MiB 513MiB
sudo parted /dev/sdb --script set 1 esp on
sudo parted /dev/sdb --script mkpart primary ext4 513MiB 100%

sudo mkfs.vfat -F32 -n ESP /dev/sdb1
sudo mkfs.ext4 -L ubuntu-usb /dev/sdb2
```

Проверка:

```bash
sudo parted /dev/sdb --script print
lsblk -f /dev/sdb
```

Должно быть две файловые системы: vfat на `sdb1`, ext4 на `sdb2`.

---

## 5. [Вручную] Монтирование и debootstrap

```bash
sudo mkdir -p /mnt/target
sudo mount /dev/sdb2 /mnt/target
sudo mkdir -p /mnt/target/boot/efi
sudo mount /dev/sdb1 /mnt/target/boot/efi

sudo debootstrap --arch=amd64 noble /mnt/target http://archive.ubuntu.com/ubuntu/
```

`debootstrap` скачает и развернёт базовую Ubuntu 24.04 на флешку. На USB 3.0 — 10–20 минут. Если ругнётся «noble not found» — обновите пакет debootstrap (в старой виртуалке мог быть без шаблона для noble):

```bash
sudo apt install -y --only-upgrade debootstrap
# или вручную:
sudo ln -s gutsy /usr/share/debootstrap/scripts/noble
```

---

## 6. [Вручную] Подготовка fstab и chroot

Сначала запишем fstab по UUID (универсальнее, чем по именам устройств):

```bash
BOOT_UUID=$(sudo blkid -s UUID -o value /dev/sdb1)
ROOT_UUID=$(sudo blkid -s UUID -o value /dev/sdb2)

sudo tee /mnt/target/etc/fstab > /dev/null <<EOF
UUID=$ROOT_UUID / ext4 defaults,noatime,errors=remount-ro 0 1
UUID=$BOOT_UUID /boot/efi vfat defaults,umask=0077 0 2
tmpfs /tmp tmpfs defaults,nosuid,nodev 0 0
EOF
```

Входим в chroot:

```bash
sudo arch-chroot /mnt/target /bin/bash
```

(Если `arch-chroot` не нашёлся — используйте ручной вариант в конце инструкции, раздел «Chroot вручную».)

**Все команды ниже — внутри chroot**, пока не выйдем через `exit`.

---

## 7. [Вручную] Настройка системы внутри chroot

### Hostname, hosts, локаль, часовой пояс

```bash
echo "ubuntu-usb" > /etc/hostname
cat > /etc/hosts <<EOF
127.0.0.1 localhost
127.0.1.1 ubuntu-usb
::1       localhost ip6-localhost ip6-loopback
ff02::1   ip6-allnodes
ff02::2   ip6-allrouters
EOF

export DEBIAN_FRONTEND=noninteractive
ln -sf /usr/share/zoneinfo/Europe/Samara /etc/localtime
```

### Репозитории

```bash
cat > /etc/apt/sources.list <<EOF
deb http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-security main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-backports main restricted universe multiverse
EOF

apt update
apt install -y locales
locale-gen en_US.UTF-8 ru_RU.UTF-8
update-locale LANG=ru_RU.UTF-8
```

### Ядро, загрузчик, сеть, базовый инструментарий

```bash
apt install -y \
  linux-generic \
  grub-efi-amd64 grub-efi-amd64-signed shim-signed efibootmgr \
  network-manager \
  sudo nano vim less curl wget ca-certificates \
  console-setup keyboard-configuration \
  openssh-server
```

`shim-signed` + подписанный GRUB нужны, если целевая машина с включённым Secure Boot — тогда флешка загрузится без отключения SB в BIOS. Если Secure Boot выключен, лишним не будет.

### Рабочее окружение (на выбор)

Полный GNOME:

```bash
apt install -y ubuntu-desktop-minimal
```

Или легче (XFCE):

```bash
apt install -y xubuntu-core
```

Или ещё легче (LXQt):

```bash
apt install -y lubuntu-desktop
```

Для флешки я бы советовал **xubuntu-core** — ощутимо быстрее на USB, чем GNOME, при полноценной графике. Если нужна «настоящая Ubuntu как с диска» — `ubuntu-desktop-minimal`.

Установка займёт 20–40 минут на USB 3.0.

### Пользователь

Создаём пользователя с совпадающим с GitHub логином:

```bash
adduser USER
usermod -aG sudo,audio,video,plugdev,netdev USER
```

Задать пароль root (на всякий случай, можно потом заблокировать):

```bash
passwd root
```

### NetworkManager — автозапуск

```bash
systemctl enable NetworkManager
systemctl enable ssh
```

---

## 8. [Вручную] Установка GRUB на флешку

Ключевой момент — **флаг `--removable`**. Он кладёт загрузчик в `/EFI/BOOT/BOOTX64.EFI` на ESP, откуда его подхватит любой UEFI без записи в NVRAM целевой машины. Без него флешка будет грузиться только на том компьютере, где её «прописали» в NVRAM.

```bash
grub-install \
  --target=x86_64-efi \
  --efi-directory=/boot/efi \
  --removable \
  --no-nvram \
  --recheck
```

`--no-nvram` — не писать в NVRAM виртуалки (бесполезно и мусор).

### Настройка grub.cfg под съёмный носитель

Правим `/etc/default/grub`, чтобы GRUB искал корень по UUID (иначе на разных машинах может сбиться нумерация дисков):

```bash
sed -i 's/^GRUB_DEFAULT=.*/GRUB_DEFAULT=0/' /etc/default/grub
sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=3/' /etc/default/grub
sed -i 's|^GRUB_CMDLINE_LINUX_DEFAULT=.*|GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"|' /etc/default/grub
sed -i 's/^GRUB_TIMEOUT_STYLE=.*/GRUB_TIMEOUT_STYLE=menu/' /etc/default/grub || \
  echo "GRUB_TIMEOUT_STYLE=menu" >> /etc/default/grub

update-grub
```

Проверка, что GRUB и ядро реально легли на ESP и корень:

```bash
ls /boot/efi/EFI/BOOT/
ls /boot/ | grep -E "vmlinuz|initrd"
```

Должны быть `BOOTX64.EFI` (и, если ставили shim, `grubx64.efi`), а в `/boot` — `vmlinuz-*` и `initrd.img-*`.

### Выход из chroot и отмонтирование

```bash
exit  # выходим из chroot
```

Теперь уже в виртуалке:

```bash
sudo umount -R /mnt/target
sync
```

`-R` рекурсивно размонтирует всё, что `arch-chroot` подмонтировал внутри. Если ругается «target is busy» — выполните `sudo lsof /mnt/target` и закройте процессы, затем повторите.

---

## 9. Передача флешки на целевую машину

1. В GUI VirtualBox на хосте: **Devices → USB → снять галочку** с вашей флешки (виртуалка её отпустит, Win7 снова увидит).
2. Либо выключите виртуалку целиком — тогда флешка автоматически вернётся в хост.
3. На хосте — «Безопасно извлечь», физически вынуть.
4. Воткнуть в целевой компьютер.
5. Включить компьютер, вызвать boot menu (обычно F12, F9, F11, Esc — зависит от материнки), выбрать флешку.
6. Если в BIOS есть вариант «UEFI: <имя флешки>» — выбирайте UEFI-вариант.

---

## 10. Первая загрузка — что должно быть

- Короткое меню GRUB (3 секунды), по Enter — старт.
- Загрузка ядра, systemd, экран входа (графический — если ставили desktop).
- Вход как `USER` под заданным паролем.
- Сеть — через NetworkManager, иконка в трее.

Что сделать сразу после первого входа:

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 11. Если целевая машина с чистым BIOS (не UEFI)

**Через скрипт** — просто добавить ключ:

```bash
sudo ./mkubuntu-usb.sh --device /dev/sdb --firmware bios
```

Остальное скрипт сделает сам: MBR вместо GPT, один раздел ext4 с флагом boot, `grub-pc` вместо EFI-пакетов, `grub-install --target=i386-pc`.

**Вручную** — заменить шаги 4 и 8 на следующее:

Разметка:

```bash
sudo wipefs -a /dev/sdb
sudo parted /dev/sdb --script mklabel msdos
sudo parted /dev/sdb --script mkpart primary ext4 1MiB 100%
sudo parted /dev/sdb --script set 1 boot on
sudo mkfs.ext4 -L ubuntu-usb /dev/sdb1
```

Монтировать и debootstrap — только корневой раздел, без `/boot/efi`:

```bash
sudo mount /dev/sdb1 /mnt/target
sudo debootstrap --arch=amd64 noble /mnt/target http://archive.ubuntu.com/ubuntu/
```

В fstab только корень:

```bash
ROOT_UUID=$(sudo blkid -s UUID -o value /dev/sdb1)
sudo tee /mnt/target/etc/fstab > /dev/null <<EOF
UUID=$ROOT_UUID / ext4 defaults,noatime,errors=remount-ro 0 1
tmpfs /tmp tmpfs defaults,nosuid,nodev 0 0
EOF
```

В chroot вместо EFI-пакетов:

```bash
apt install -y grub-pc
```

GRUB ставить так:

```bash
grub-install --target=i386-pc --recheck /dev/sdb
update-grub
```

---

## 12. Chroot вручную (если `arch-chroot` недоступен)

Вместо `sudo arch-chroot /mnt/target /bin/bash`:

```bash
sudo mount --bind /dev  /mnt/target/dev
sudo mount --bind /dev/pts /mnt/target/dev/pts
sudo mount --bind /proc /mnt/target/proc
sudo mount --bind /sys  /mnt/target/sys
sudo mount --bind /run  /mnt/target/run
sudo cp /etc/resolv.conf /mnt/target/etc/resolv.conf

sudo chroot /mnt/target /bin/bash
```

После выхода из chroot — размонтировать в обратном порядке (или `sudo umount -R /mnt/target`).

---

## 13. Типичные грабли

- **Виртуалка не видит флешку.** Extension Pack не той версии / не установлен; USB-контроллер в настройках виртуалки отключён; фильтр не добавлен; Win7 держит флешку занятой (откройте «Безопасное извлечение» на хосте).
- **`sdb` на самом деле не флешка.** Если в виртуалке подключены ещё диски (shared disk, snapshot), флешка может оказаться `sdc`. Всегда проверяйте `lsblk` перед разметкой. Скрипт откажется работать, если указать корневой диск, но на другие доп. диски не проверяет — внимание всё равно нужно.
- **`debootstrap: noble not found`.** Пакет debootstrap в виртуалке старее кодового имени 24.04 → обновить, или сделать симлинк (см. шаг 5). Скрипт обходит это сам.
- **`grub-install` ругается на efi-directory.** Не смонтирован `/boot/efi` внутри chroot. Проверьте `mount | grep efi` — если пусто, выйдите, перемонтируйте, зайдите снова.
- **На целевой машине флешки нет в boot menu.** Включите в BIOS загрузку с USB и Legacy/UEFI в соответствии со схемой разметки. Для UEFI убедитесь, что флешка в режиме UEFI (не Legacy) в boot menu.
- **GRUB появился, но ядро не стартует.** Обычно `fstab` с неправильным UUID или не установлен `linux-generic`. Можно загрузиться с live-флешки, chroot в флешку, `apt install --reinstall linux-generic`, `update-grub`.
- **Чёрный экран после GRUB.** Чаще всего — отсутствует проприетарный драйвер NVIDIA (если на целевой машине NVIDIA). При первой загрузке попробуйте добавить `nomodeset` в параметры ядра через меню GRUB (клавиша `e`, допишите в строку `linux ...`). После входа — поставить `nvidia-driver-535` или свежее.
- **Медленно.** Флешка USB 2.0 или дешёвая USB 3.0 без SLC-кэша. Решение одно — лучшая флешка (Samsung FIT Plus, SanDisk Extreme). Для корректного сравнения — `sudo hdparm -t /dev/sdb` на холодную.
