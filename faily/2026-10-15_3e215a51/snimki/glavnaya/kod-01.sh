echo "ubuntu-usb" > /etc/hostname
cat > /etc/apt/sources.list <<EOF
deb http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu noble-security main restricted universe multiverse
EOF

apt update
apt install -y linux-generic grub-efi-amd64 network-manager sudo nano
# для рабочего стола — любой на выбор:
apt install -y ubuntu-desktop-minimal
# или легче:
# apt install -y xubuntu-desktop  (XFCE)
# apt install -y lubuntu-desktop  (LXQt)