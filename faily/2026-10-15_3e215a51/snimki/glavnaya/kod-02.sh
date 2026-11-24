# внутри chroot
BOOT_UUID=$(blkid -s UUID -o value /dev/sdb1)
ROOT_UUID=$(blkid -s UUID -o value /dev/sdb2)

cat > /etc/fstab <<EOF
UUID=$ROOT_UUID / ext4 defaults,noatime 0 1
UUID=$BOOT_UUID /boot/efi vfat defaults 0 2
EOF

adduser User
usermod -aG sudo User
passwd root