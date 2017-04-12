#!/usr/bin/env python

import sys
import json
import argparse
import subprocess

def run_qemu(topo, vm, foreground):
    nics = []
    vlans = set()
    cmds = []
    for v in topo['vms']:
        if 'loopback_ip' in v:
            cmds.append('echo %s %s >> /etc/hosts' % (v['loopback_ip'], v['hostname']))
        for (index, nic) in enumerate(v['interfaces']):
            if 'ip' in nic:
                cmds.append('echo %s %s-%s >> /etc/hosts' % (nic['ip'], v['hostname'], index))

    cmds.append('echo %s > /etc/hostname; hostname -F /etc/hostname' % vm['hostname'])
    if 'loopback_ip' in vm:
        cmds.append('ip addr add %s dev lo' % vm['loopback_ip'])
    for (index, nic) in enumerate(vm['interfaces']):
        nics.append('-net nic,macaddr=00:00:00:00:00:%s,vlan=%s' % (nic['mac'], nic['vlan']))
        if nic['vlan'] not in vlans:
            nics.append('-net bridge,br=virbr%s,vlan=%s' % (nic['vlan'], nic['vlan']))
            vlans.add(nic['vlan'])
        if 'ip' in nic:
            cmds.append('ip addr add %s dev eth%s' % (nic['ip'], index))
        if 'routes' in nic:
            for route in nic['routes']:
                via = ip_from_mac(route['via'])
                cmds.append('ip route add %s via %s dev eth%s' % (route['prefix'], via, index))
    fore = '-nographic' if foreground else '-display none -daemonize'
    open('cmds', 'w').write('\n'.join(cmds) + '\n')
    subprocess.call(
        '/bin/bash -c \'qemu-system-x86_64 -enable-kvm -m 512 ' + fore + ' -kernel deboot-master/boot/vmlinuz-4.4.0-21-generic -initrd deboot-master/boot/initrd.img-4.4.0-21-generic -hda master.img -snapshot -hdb cmds -append "root=/dev/sda1 console=ttyS0 net.ifnames=0" -monitor pty ' + ' '.join(nics) + '; rm cmds\'', shell=True)

def ip_for_iface(iface):
    ip = ip_from_mac(iface['mac'])
    br = 'virbr%s' % iface['vlan']
    return '%s%%%s' % (ip, br)

def ip_from_mac(mac):
    return 'fe80::0200:ff:fe00:00%s' % mac

def find_vm(topo, hostname):
    return [vm for vm in topo['vms'] if vm['hostname'] == hostname][0]

def iface_from_hostname(topo, hostname):
    return find_vm(topo, hostname)['interfaces'][0]

def cmd_run(topo, args):
    if args.vm is None:
        # run all in background
        for vm in topo['vms']:
           run_qemu(topo, vm, foreground=False)
    else:
        vm = find_vm(topo, args.vm)
        run_qemu(topo, vm, foreground=True)

def cmd_kill(topo, args):
    # not _64 because cmd line length is <= 15
    subprocess.call('pkill -INT -x qemu-system-x86', shell=True)

def cmd_ping(topo, args):
    iface = iface_from_hostname(topo, args.vm)
    subprocess.call('ping6 -c1 %s' % ip_for_iface(iface), shell=True)

def cmd_ssh(topo, args):
    iface = iface_from_hostname(topo, args.vm)
    subprocess.call('ssh root@%s' % ip_for_iface(iface), shell=True)

def cmd_wait(topo, args):
    def wait_one(hostname):
        iface = iface_from_hostname(topo, hostname)
        while subprocess.call('ping6 -c1 %s' % ip_for_iface(iface), shell=True) != 0:
            pass

    if args.vm is None:
        for vm in topo['vms']:
            wait_one(vm['hostname'])
    else:
        wait_one(args.vm)

def cmd_list(topo, args):
    # not _64 because cmd line length is <= 15
    subprocess.call('pgrep -lx qemu-system-x86', shell=True)

def cmd_cmd(topo, args):
    iface = iface_from_hostname(topo, args.vm)
    cmd = "' '".join(args.cmd)
    subprocess.call('ssh root@%s \'%s\'' % (ip_for_iface(iface), cmd), shell=True)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('vm', nargs='?')
    parser_run.set_defaults(func=cmd_run)
    parser_kill = subparsers.add_parser('kill')
    parser_kill.set_defaults(func=cmd_kill)
    parser_ping = subparsers.add_parser('ping')
    parser_ping.add_argument('vm')
    parser_ping.set_defaults(func=cmd_ping)
    parser_ssh = subparsers.add_parser('ssh')
    parser_ssh.add_argument('vm')
    parser_ssh.set_defaults(func=cmd_ssh)
    parser_wait = subparsers.add_parser('wait')
    parser_wait.add_argument('vm', nargs='?')
    parser_wait.set_defaults(func=cmd_wait)
    parser_list = subparsers.add_parser('list')
    parser_list.set_defaults(func=cmd_list)
    parser_cmd = subparsers.add_parser('cmd')
    parser_cmd.add_argument('vm')
    parser_cmd.add_argument('cmd', nargs='+')
    parser_cmd.set_defaults(func=cmd_cmd)

    with open('topo') as f:
        topo = json.load(f)

    args = parser.parse_args()
    args.func(topo, args)

if __name__ == '__main__':
    main()
