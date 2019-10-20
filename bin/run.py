#!/usr/bin/env python

""" Download files and run setup VM """

from fetch import *
import os
import sys

VERSION='10.15.1'
DIR_DISKS=os.path.realpath('./disks')
DIR_OVM=os.path.realpath('./firmware')

DISK_SYSTEM='%s/System-%s.qcow2' % (DIR_DISKS, VERSION)
DISK_ESP='%s/ESP.qcow2' % DIR_DISKS
OVM_CODE='%s/OVMF_CODE.fd' % DIR_OVM
OVM_VARS='%s/OVMF_VARS-1024x768.fd' % DIR_OVM

# openssl rand -hex 6 | sed 's/\(..\)/\1:/g; s/.$//'
MAC_ADDRESS='a0:9f:de:46:89:2b'
SIZE_MEMORY='2G'
SIZE_SYSTEM='64G'

run([
  'qemu-system-x86_64',
  '-enable-kvm',
  '-m', MEMORY, 
  '-machine', 'q35,accel=kvm',
  '-smp', '4,cores=2', 
  '-cpu', 'Penryn,vendor=GenuineIntel,kvm=on,+sse3,+sse4.2,+aes,+xsave,+avx,+xsaveopt,+xsavec,+xgetbv1,+avx2,+bmi2,+smep,+bmi1,+fma,+movbe,+invtsc',
  '-device', 'isa-applesmc,osk=ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc',
  '-smbios', 'type=2',
  '-drive', 'if=pflash,format=raw,readonly,file=%s' % OVM_CODE,
  '-drive', 'if=pflash,format=raw,file=%s' % OVM_VARS,
  '-vga', 'qxl',
  '-device', 'ich9-intel-hda',
  '-device', 'hda-output',
  '-usb', '-device', 'usb-kbd',
  '-device', 'usb-mouse',
  '-netdev', 'user,id=net0',
  '-device', 'e1000-82545em,netdev=net0,id=net0,mac=%s' % MAC_ADDRESS,
  '-device', 'ich9-ahci,id=sata',
  '-drive', 'id=ESP,if=none,format=qcow2,file=%s' % DISK_ESP,
  '-device', 'ide-hd,bus=sata.2,drive=ESP',
  '-drive', 'id=SYSTEM,format=qcow2,if=none,file=%s' % DISK_SYSTEM,
  '-device', 'ide-hd,bus=sata.4,drive=SYSTEM'
])
