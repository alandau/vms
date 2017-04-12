#!/bin/sh

DIR=deboot-master
sudo sh <<EOF
echo vm > $DIR/etc/hostname
> $DIR/etc/resolv.conf
sed -i -e 's/PermitRootLogin .*/PermitRootLogin yes/' \
  -e 's/PermitEmptyPasswords .*/PermitEmptyPasswords yes/' \
  -e 's/UsePAM .*/UsePAM no/' \
  $DIR/etc/ssh/sshd_config
sed -i 's/root:x:/root::/' $DIR/etc/shadow
grep -q '/dev/sda1' $DIR/etc/fstab 2>/dev/null || echo '/dev/sda1 / ext2 defaults,rw' >> $DIR/etc/fstab
echo net.ipv6.conf.all.forwarding=1 > $DIR/etc/sysctl.d/90-custom.conf
echo net.ipv4.ip_forward=1 >> $DIR/etc/sysctl.d/90-custom.conf

cat <<'RC' > $DIR/etc/rc.local
#!/bin/sh
for i in \`ls /sys/class/net\`; do ip link set dev \$i up; done
cat /dev/sdb > /run/autorun || exit 0
cd /run
sh autorun
exit 0
RC
chmod +x $DIR/etc/rc.local
EOF
