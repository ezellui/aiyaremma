#!/bin/bash
# mkubuntu-usb.sh — сборка полноценной Ubuntu на USB-флешке через debootstrap
# Запускать внутри гостевой Ubuntu Server, где флешка уже проброшена из VirtualBox.
#
# Пример:
#   sudo ./mkubuntu-usb.sh --device /dev/sdb --user USER --hostname ubuntu-usb
#
# С обменным разделом (видимым из Windows/Android):
#   sudo ./mkubuntu-usb.sh --device /dev/sdb --data-size 32GiB
#
# Проверить, что доступно:
#   ./mkubuntu-usb.sh --help

set -euo pipefail

# ============================================================
# Значения по умолчанию
# ============================================================

DEVICE=""
USERNAME="USER"
HOSTNAME="ubuntu-usb"
SUITE="noble"
ARCH="amd64"
MIRROR="http://archive.ubuntu.com/ubuntu/"
TIMEZONE="Europe/Samara"
LOCALES="en_US.UTF-8 ru_RU.UTF-8"
DEFAULT_LOCALE="ru_RU.UTF-8"
DESKTOP="xubuntu-core"   # варианты: ubuntu-desktop-minimal | xubuntu-core | lubuntu-desktop | none
FIRMWARE_MODE="uefi"     # варианты: uefi | bios
MOUNT_POINT="/mnt/target"
ASSUME_YES="no"

# Обменный раздел (видимый из Windows/Android)
DATA_SIZE=""             # "0" или пусто = не делать; иначе напр. "32GiB", "16GiB"
DATA_FS="exfat"          # exfat (default) | fat32
DATA_LABEL="SHARED"
DATA_MOUNT="/media/shared"

# ============================================================
# Разбор аргументов
# ============================================================

print_help() {
    cat <<'EOF'
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
  --mount-point PATH     Куда монтировать флешку при сборке
                         (default: /mnt/target)

Обменный раздел (видимый из Windows/Android/macOS):
  --data-size SIZE       Размер обменного раздела, напр. 32GiB, 16GiB, 50%.
                         Если не задан или 0 — обменного раздела не будет.
                         Раздел создаётся ПЕРВЫМ на флешке, для совместимости
                         со старыми Android.
  --data-fs FS           Файловая система обменного раздела:
                           exfat (default) — без лимита 4 ГБ на файл,
                                             нужен Android 7+/Win10/macOS 10.6+
                           fat32           — максимальная совместимость,
                                             но файлы > 4 ГБ не поддерживаются
  --data-label NAME      Метка обменного раздела (default: SHARED)
  --data-mount PATH      Точка монтирования внутри Ubuntu
                         (default: /media/shared)

Прочее:
  -y, --yes              Не спрашивать подтверждения перед разметкой
  -h, --help             Показать эту справку

Примеры:
  # Простая сборка без обменного раздела
  sudo ./mkubuntu-usb.sh --device /dev/sdb

  # 64 ГБ флешка: 32 ГБ exFAT (обмен) + ESP + остаток под Ubuntu
  sudo ./mkubuntu-usb.sh --device /dev/sdb --data-size 32GiB

  # Своё имя пользователя и легковесный desktop
  sudo ./mkubuntu-usb.sh --device /dev/sdb --user alice \
                         --desktop lubuntu-desktop --data-size 16GiB

  # Для старого Android, который не умеет exFAT
  sudo ./mkubuntu-usb.sh --device /dev/sdb --data-size 20GiB --data-fs fat32

  # BIOS-only целевая машина, без desktop, без подтверждения
  sudo ./mkubuntu-usb.sh --device /dev/sdb --firmware bios --desktop none -y
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --device)         DEVICE="$2"; shift 2 ;;
        --user)           USERNAME="$2"; shift 2 ;;
        --hostname)       HOSTNAME="$2"; shift 2 ;;
        --suite)          SUITE="$2"; shift 2 ;;
        --arch)           ARCH="$2"; shift 2 ;;
        --mirror)         MIRROR="$2"; shift 2 ;;
        --timezone)       TIMEZONE="$2"; shift 2 ;;
        --locales)        LOCALES="$2"; shift 2 ;;
        --default-locale) DEFAULT_LOCALE="$2"; shift 2 ;;
        --desktop)        DESKTOP="$2"; shift 2 ;;
        --firmware)       FIRMWARE_MODE="$2"; shift 2 ;;
        --mount-point)    MOUNT_POINT="$2"; shift 2 ;;
        --data-size)      DATA_SIZE="$2"; shift 2 ;;
        --data-fs)        DATA_FS="$2"; shift 2 ;;
        --data-label)     DATA_LABEL="$2"; shift 2 ;;
        --data-mount)     DATA_MOUNT="$2"; shift 2 ;;
        -y|--yes)         ASSUME_YES="yes"; shift ;;
        -h|--help)        print_help; exit 0 ;;
        *) echo "Неизвестный аргумент: $1" >&2; print_help; exit 2 ;;
    esac
done

# ============================================================
# Вспомогательные функции
# ============================================================

log()   { printf '\n\033[1;36m[%s]\033[0m %s\n' "$(date +%H:%M:%S)" "$*"; }
warn()  { printf '\n\033[1;33m[WARN]\033[0m %s\n' "$*" >&2; }
die()   { printf '\n\033[1;31m[FATAL]\033[0m %s\n' "$*" >&2; exit 1; }

cleanup() {
    local rc=$?
    if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
        log "Отмонтирую $MOUNT_POINT (cleanup)…"
        umount -R "$MOUNT_POINT" 2>/dev/null || true
    fi
    exit $rc
}
trap cleanup EXIT INT TERM

# Нормализация флага «делать ли обменный раздел»
WANT_DATA="no"
if [[ -n "$DATA_SIZE" && "$DATA_SIZE" != "0" ]]; then
    WANT_DATA="yes"
fi

# ============================================================
# Проверки окружения
# ============================================================

[[ $EUID -eq 0 ]] || die "Нужен root. Запускай через sudo."

[[ -n "$DEVICE" ]] || { print_help; die "Не задан --device"; }
[[ -b "$DEVICE" ]] || die "$DEVICE не блочное устройство"

case "$FIRMWARE_MODE" in uefi|bios) ;; *) die "--firmware должен быть uefi или bios" ;; esac
case "$DESKTOP" in ubuntu-desktop-minimal|xubuntu-core|lubuntu-desktop|none) ;; *) die "--desktop: недопустимое значение '$DESKTOP'" ;; esac
if [[ "$WANT_DATA" == "yes" ]]; then
    case "$DATA_FS" in exfat|fat32|vfat) ;; *) die "--data-fs должен быть exfat или fat32" ;; esac
fi

# Защита от выбора системного диска
ROOT_SRC=$(findmnt -no SOURCE / | sed 's/[0-9]*$//')
if [[ "$DEVICE" == "$ROOT_SRC" ]]; then
    die "$DEVICE — это текущий корневой диск! Отказ."
fi

# Проверка, что устройство — USB (мягкая, но полезная)
if command -v lsblk >/dev/null; then
    TRAN=$(lsblk -ndo TRAN "$DEVICE" 2>/dev/null || echo "")
    if [[ "$TRAN" != "usb" ]]; then
        warn "$DEVICE не USB (TRAN='$TRAN'). Уверен, что это та флешка?"
    fi
fi

# Проверка нужных утилит
NEEDED=(debootstrap parted mkfs.vfat mkfs.ext4 blkid wipefs arch-chroot)
if [[ "$WANT_DATA" == "yes" && "$DATA_FS" == "exfat" ]]; then
    NEEDED+=(mkfs.exfat)
fi

MISSING=()
for cmd in "${NEEDED[@]}"; do
    command -v "$cmd" >/dev/null || MISSING+=("$cmd")
done
if (( ${#MISSING[@]} )); then
    log "Доставляю недостающие пакеты: ${MISSING[*]}"
    apt-get update
    EXTRA_PKGS=()
    [[ "$WANT_DATA" == "yes" && "$DATA_FS" == "exfat" ]] && EXTRA_PKGS+=(exfatprogs)
    apt-get install -y debootstrap parted dosfstools arch-install-scripts "${EXTRA_PKGS[@]}"
fi

# ============================================================
# Подтверждение
# ============================================================

echo
echo "=========================================================="
echo "  Устройство:     $DEVICE  (будет затёрто!)"
lsblk -o NAME,SIZE,TYPE,MODEL,SERIAL "$DEVICE" || true
echo "  Прошивка:       $FIRMWARE_MODE"
echo "  Пользователь:   $USERNAME"
echo "  Hostname:       $HOSTNAME"
echo "  Релиз:          $SUITE ($ARCH)"
echo "  Зеркало:        $MIRROR"
echo "  TZ / locale:    $TIMEZONE / $DEFAULT_LOCALE"
echo "  Desktop:        $DESKTOP"
echo "  Точка монт.:    $MOUNT_POINT"
if [[ "$WANT_DATA" == "yes" ]]; then
    echo "  Обменный:       $DATA_SIZE  $DATA_FS  label='$DATA_LABEL'  → $DATA_MOUNT"
else
    echo "  Обменный:       (нет)"
fi
echo "=========================================================="
echo

if [[ "$ASSUME_YES" != "yes" ]]; then
    read -r -p "Продолжить? Все данные на $DEVICE будут уничтожены. [yes/NO]: " ANS
    [[ "$ANS" == "yes" ]] || die "Отменено пользователем."
fi

# ============================================================
# Разметка
# ============================================================

log "Размонтирую возможные старые разделы с $DEVICE…"
for part in $(lsblk -lnpo NAME "$DEVICE" | tail -n +2); do
    umount "$part" 2>/dev/null || true
done

log "Затираю таблицу разделов на $DEVICE…"
wipefs -a "$DEVICE"

# Префикс имён разделов: /dev/sdb → sdb1; /dev/nvme0n1 → nvme0n1p1
probe_prefix() {
    # После создания разделов узнаем, нужна ли p-нотация
    if [[ -b "${DEVICE}p1" ]]; then
        echo "${DEVICE}p"
    else
        echo "${DEVICE}"
    fi
}

DATA_PART=""
ESP_PART=""
ROOT_PART=""

# Вычислить конец раздела как START + 513 MiB (для ESP сразу после обменного)
calc_esp_end() {
    local start="$1"
    python3 -c "
import re, sys
m = re.match(r'^([\d.]+)(KiB|MiB|GiB|TiB)?\$', '$start')
if not m:
    print('ERR: bad size: $start', file=sys.stderr); sys.exit(1)
v = float(m.group(1)); u = m.group(2) or 'MiB'
mult = {'KiB':1024,'MiB':1024**2,'GiB':1024**3,'TiB':1024**4}[u]
end_bytes = int(v*mult) + 513*1024*1024
print(f'{end_bytes // (1024*1024)}MiB')
"
}

if [[ "$FIRMWARE_MODE" == "uefi" ]]; then
    if [[ "$WANT_DATA" == "yes" ]]; then
        log "Разметка GPT: обмен ($DATA_FS, $DATA_SIZE) + ESP (512 МБ FAT32) + root (ext4)…"
        ESP_END=$(calc_esp_end "$DATA_SIZE")
        # Обменный раздел идёт первым — для совместимости со старыми Android,
        # которые видят только первый раздел съёмного носителя
        parted "$DEVICE" --script mklabel gpt
        parted "$DEVICE" --script mkpart "$DATA_LABEL" 1MiB "$DATA_SIZE"
        parted "$DEVICE" --script mkpart ESP fat32 "$DATA_SIZE" "$ESP_END"
        parted "$DEVICE" --script set 2 esp on
        parted "$DEVICE" --script mkpart primary ext4 "$ESP_END" 100%
        partprobe "$DEVICE" || true
        sleep 1
        PREFIX=$(probe_prefix)
        DATA_PART="${PREFIX}1"
        ESP_PART="${PREFIX}2"
        ROOT_PART="${PREFIX}3"
    else
        log "Разметка GPT: ESP (512 МБ FAT32) + root (ext4)…"
        parted "$DEVICE" --script mklabel gpt
        parted "$DEVICE" --script mkpart ESP fat32 1MiB 513MiB
        parted "$DEVICE" --script set 1 esp on
        parted "$DEVICE" --script mkpart primary ext4 513MiB 100%
        partprobe "$DEVICE" || true
        sleep 1
        PREFIX=$(probe_prefix)
        ESP_PART="${PREFIX}1"
        ROOT_PART="${PREFIX}2"
    fi
else
    # BIOS / MBR
    if [[ "$WANT_DATA" == "yes" ]]; then
        log "Разметка MBR: обмен ($DATA_FS, $DATA_SIZE) + root (ext4, boot)…"
        parted "$DEVICE" --script mklabel msdos
        parted "$DEVICE" --script mkpart primary 1MiB "$DATA_SIZE"
        parted "$DEVICE" --script mkpart primary ext4 "$DATA_SIZE" 100%
        parted "$DEVICE" --script set 2 boot on
        partprobe "$DEVICE" || true
        sleep 1
        PREFIX=$(probe_prefix)
        DATA_PART="${PREFIX}1"
        ROOT_PART="${PREFIX}2"
    else
        log "Разметка MBR: один раздел ext4 с флагом boot…"
        parted "$DEVICE" --script mklabel msdos
        parted "$DEVICE" --script mkpart primary ext4 1MiB 100%
        parted "$DEVICE" --script set 1 boot on
        partprobe "$DEVICE" || true
        sleep 1
        PREFIX=$(probe_prefix)
        ROOT_PART="${PREFIX}1"
    fi
fi

# ============================================================
# Форматирование
# ============================================================

if [[ -n "$DATA_PART" ]]; then
    log "Форматирую обменный раздел $DATA_PART как $DATA_FS…"
    case "$DATA_FS" in
        exfat)
            mkfs.exfat -L "$DATA_LABEL" "$DATA_PART"
            ;;
        fat32|vfat)
            mkfs.vfat -F32 -n "${DATA_LABEL:0:11}" "$DATA_PART"
            ;;
    esac
fi

if [[ -n "$ESP_PART" ]]; then
    log "Форматирую ESP $ESP_PART как FAT32…"
    mkfs.vfat -F32 -n ESP "$ESP_PART"
fi

log "Форматирую корень $ROOT_PART как ext4…"
mkfs.ext4 -F -L ubuntu-usb "$ROOT_PART"

# ============================================================
# Монтирование
# ============================================================

log "Монтирую корень в $MOUNT_POINT…"
mkdir -p "$MOUNT_POINT"
mount "$ROOT_PART" "$MOUNT_POINT"

if [[ -n "$ESP_PART" ]]; then
    mkdir -p "$MOUNT_POINT/boot/efi"
    mount "$ESP_PART" "$MOUNT_POINT/boot/efi"
fi

# ============================================================
# debootstrap
# ============================================================

log "debootstrap: разворачиваю базовую $SUITE в $MOUNT_POINT (это долго)…"
if ! debootstrap --arch="$ARCH" "$SUITE" "$MOUNT_POINT" "$MIRROR"; then
    warn "debootstrap не знает '$SUITE'. Пробую обойти символической ссылкой."
    if [[ ! -f "/usr/share/debootstrap/scripts/$SUITE" ]]; then
        ln -sf gutsy "/usr/share/debootstrap/scripts/$SUITE"
    fi
    debootstrap --arch="$ARCH" "$SUITE" "$MOUNT_POINT" "$MIRROR"
fi

# ============================================================
# fstab
# ============================================================

log "Пишу fstab по UUID…"
ROOT_UUID=$(blkid -s UUID -o value "$ROOT_PART")

{
    echo "UUID=$ROOT_UUID / ext4 defaults,noatime,errors=remount-ro 0 1"
    if [[ -n "$ESP_PART" ]]; then
        ESP_UUID=$(blkid -s UUID -o value "$ESP_PART")
        echo "UUID=$ESP_UUID /boot/efi vfat defaults,umask=0077 0 2"
    fi
    if [[ -n "$DATA_PART" ]]; then
        DATA_UUID=$(blkid -s UUID -o value "$DATA_PART")
        case "$DATA_FS" in
            exfat)
                # uid/gid 1000 — первый созданный пользователь (adduser даёт ему 1000)
                echo "UUID=$DATA_UUID $DATA_MOUNT exfat rw,uid=1000,gid=1000,umask=0022,nofail 0 0"
                ;;
            fat32|vfat)
                echo "UUID=$DATA_UUID $DATA_MOUNT vfat rw,uid=1000,gid=1000,umask=0022,nofail 0 0"
                ;;
        esac
    fi
    echo "tmpfs /tmp tmpfs defaults,nosuid,nodev 0 0"
} | tee "$MOUNT_POINT/etc/fstab" >/dev/null

# Создать точку монтирования для обменного раздела заранее
if [[ -n "$DATA_PART" ]]; then
    mkdir -p "$MOUNT_POINT$DATA_MOUNT"
fi

# ============================================================
# Chroot — настройка системы
# ============================================================

log "Готовлю inside-скрипт для chroot…"

INSIDE="$MOUNT_POINT/root/inside.sh"
cat > "$INSIDE" <<INSIDE_EOF
#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export LANG=C

HOSTNAME="$HOSTNAME"
USERNAME="$USERNAME"
TIMEZONE="$TIMEZONE"
LOCALES="$LOCALES"
DEFAULT_LOCALE="$DEFAULT_LOCALE"
SUITE="$SUITE"
MIRROR="$MIRROR"
DESKTOP="$DESKTOP"
FIRMWARE_MODE="$FIRMWARE_MODE"
WANT_DATA="$WANT_DATA"
DATA_FS="$DATA_FS"

echo "=> hostname / hosts"
echo "\$HOSTNAME" > /etc/hostname
cat > /etc/hosts <<HOSTS
127.0.0.1 localhost
127.0.1.1 \$HOSTNAME
::1       localhost ip6-localhost ip6-loopback
ff02::1   ip6-allnodes
ff02::2   ip6-allrouters
HOSTS

echo "=> timezone"
ln -sf "/usr/share/zoneinfo/\$TIMEZONE" /etc/localtime

echo "=> sources.list"
cat > /etc/apt/sources.list <<SRC
deb \$MIRROR \$SUITE main restricted universe multiverse
deb \$MIRROR \$SUITE-updates main restricted universe multiverse
deb \$MIRROR \$SUITE-security main restricted universe multiverse
deb \$MIRROR \$SUITE-backports main restricted universe multiverse
SRC

echo "=> apt update + базовые пакеты"
apt-get update
apt-get install -y locales
locale-gen \$LOCALES
update-locale LANG=\$DEFAULT_LOCALE

echo "=> ядро + загрузчик + инструменты"
BASE_PKGS="linux-generic network-manager sudo nano vim less curl wget ca-certificates \
console-setup keyboard-configuration openssh-server tzdata"
if [[ "\$FIRMWARE_MODE" == "uefi" ]]; then
    BOOT_PKGS="grub-efi-amd64 grub-efi-amd64-signed shim-signed efibootmgr"
else
    BOOT_PKGS="grub-pc"
fi

# Поддержка exFAT, если обменный раздел задан
EXTRA_PKGS=""
if [[ "\$WANT_DATA" == "yes" && "\$DATA_FS" == "exfat" ]]; then
    EXTRA_PKGS="exfatprogs"
fi

apt-get install -y \$BASE_PKGS \$BOOT_PKGS \$EXTRA_PKGS

echo "=> рабочее окружение: \$DESKTOP"
case "\$DESKTOP" in
    none) : ;;
    *) apt-get install -y "\$DESKTOP" ;;
esac

echo "=> пользователь \$USERNAME"
if ! id "\$USERNAME" >/dev/null 2>&1; then
    adduser --gecos "" --disabled-password "\$USERNAME"
    echo "   Задай пароль для \$USERNAME:"
    passwd "\$USERNAME"
fi
usermod -aG sudo,audio,video,plugdev,netdev "\$USERNAME"

echo "=> включаю службы"
systemctl enable NetworkManager
systemctl enable ssh

echo "=> GRUB"
if [[ "\$FIRMWARE_MODE" == "uefi" ]]; then
    grub-install --target=x86_64-efi --efi-directory=/boot/efi \
                 --removable --no-nvram --recheck
else
    grub-install --target=i386-pc --recheck "$DEVICE"
fi

# Нормальное меню, timeout 3 c
sed -i 's/^GRUB_DEFAULT=.*/GRUB_DEFAULT=0/' /etc/default/grub
sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=3/' /etc/default/grub
sed -i 's|^GRUB_CMDLINE_LINUX_DEFAULT=.*|GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"|' /etc/default/grub
if grep -q '^GRUB_TIMEOUT_STYLE=' /etc/default/grub; then
    sed -i 's/^GRUB_TIMEOUT_STYLE=.*/GRUB_TIMEOUT_STYLE=menu/' /etc/default/grub
else
    echo "GRUB_TIMEOUT_STYLE=menu" >> /etc/default/grub
fi

update-grub

echo "=> проверка, что ядро и загрузчик на месте:"
ls /boot/ | grep -E "vmlinuz|initrd" || true
if [[ "\$FIRMWARE_MODE" == "uefi" ]]; then
    ls /boot/efi/EFI/BOOT/ || true
fi

echo "=> готово внутри chroot"
INSIDE_EOF

chmod +x "$INSIDE"

log "Вхожу в chroot и запускаю настройку…"
arch-chroot "$MOUNT_POINT" /root/inside.sh

log "Чищу inside-скрипт"
rm -f "$INSIDE"

# ============================================================
# Отмонтирование
# ============================================================

log "Отмонтирую $MOUNT_POINT…"
sync
umount -R "$MOUNT_POINT"
trap - EXIT

echo
echo "=========================================================="
echo "  Готово."
if [[ "$WANT_DATA" == "yes" ]]; then
    echo "  Разметка:"
    echo "    $DATA_PART  — $DATA_FS, label '$DATA_LABEL'  (обмен; виден везде)"
    [[ -n "$ESP_PART" ]] && echo "    $ESP_PART  — FAT32 ESP"
    echo "    $ROOT_PART  — ext4 Ubuntu"
    echo "  При загрузке Ubuntu обменный раздел будет смонтирован"
    echo "  в $DATA_MOUNT (с правами пользователя uid=1000)."
fi
echo
echo "  Теперь: Devices → USB → снять галочку с флешки в GUI"
echo "  VirtualBox (или просто выключить виртуалку), 'Безопасно"
echo "  извлечь' на хосте, нести на целевую машину и грузиться"
echo "  через boot menu."
echo "=========================================================="
