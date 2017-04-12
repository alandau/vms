#!/bin/sh

DIR=deboot-master
sudo rm -rf $DIR/dev
sudo debootstrap --arch=amd64 --variant=minbase --keep-debootstrap-dir \
  --include=linux-image-4.8.0-22-generic,initramfs-tools,openssh-server,systemd-sysv,less,iproute2,net-tools,iputils-ping,inetutils-traceroute,netcat-openbsd,tcpdump,traceroute,strace,iptables \
  --components=main,universe \
  yakkety $DIR http://us.archive.ubuntu.com/ubuntu
sudo chmod 644 $DIR/boot/vmlinuz*
