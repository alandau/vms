#!/bin/sh

set -e 

trap 'sudo umount mnt; rmdir mnt; sudo losetup -d /dev/loop0' EXIT
rm -f master.img
qemu-img create -f raw master.img 1G
echo ';' | sfdisk master.img
sudo losetup -P /dev/loop0 master.img
sudo mke2fs /dev/loop0p1
mkdir -p mnt
sudo mount /dev/loop0p1 mnt
sudo cp -a deboot-master/* mnt
