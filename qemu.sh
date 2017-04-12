#!/bin/sh

qemu-system-x86_64 -m 512 -nographic -kernel deboot-master/boot/vmlinuz-4.8.0-22-generic -initrd deboot-master/boot/initrd.img-4.8.0-22-generic -hda master.img -snapshot -append "root=/dev/sda1 console=ttyS0" -net nic,macaddr=00:00:00:00:00:01 -net bridge,br=virbr0

#qemu-system-x86_64 -m 512 -nographic -kernel deboot-master/boot/vmlinuz-4.8.0-22-generic -initrd deboot-master/boot/initrd.img-4.8.0-22-generic -hda master.img -snapshot -append "root=/dev/sda1 console=ttyS0" -net nic,mac=00:00:00:22:22:22 -net bridge,br=virbr0
