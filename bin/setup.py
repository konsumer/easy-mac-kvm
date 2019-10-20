#!/usr/bin/env python

""" Download files and run setup VM """

from fetch import *
import os
import sys

VERSION='10.15.1'
DIR_DISKS=os.path.realpath('./disks')
DIR_OVM=os.path.realpath('./firmware')

DISK_SYSTEM='%s/System-%s.qcow2' % (DIR_DISKS, VERSION)
DISK_INSTALLER='%s/Installer-%s.img' % (DIR_DISKS, VERSION)
DISK_ESP='%s/ESP.qcow2' % DIR_DISKS
OVM_CODE='%s/OVMF_CODE.fd' % DIR_OVM
OVM_VARS='%s/OVMF_VARS-1024x768.fd' % DIR_OVM

# openssl rand -hex 6 | sed 's/\(..\)/\1:/g; s/.$//'
MAC_ADDRESS='a0:9f:de:46:89:2b'
MEMORY='2G'

mkdir_p(DIR_DISKS)
mkdir_p(DIR_OVM)

getInstaller(VERSION, DISK_INSTALLER)

if not os.path.exists(DISK_SYSTEM):
  run(['qemu-img', 'create', '-f', 'qcow2', DISK_SYSTEM, '64G'])

if not os.path.exists(OVM_CODE):
  download('https://github.com/kholia/OSX-KVM/raw/master/OVMF_CODE.fd', OVM_CODE)

if not os.path.exists(OVM_VARS):
  download('https://github.com/kholia/OSX-KVM/raw/master/OVMF_VARS-1024x768.fd', OVM_VARS)

if not os.path.exists(DISK_ESP):
  download('https://github.com/foxlet/macOS-Simple-KVM/raw/master/ESP.qcow2', DISK_ESP)


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
  '-drive', 'id=INSTALLER,format=raw,if=none,file=%s' % DISK_INSTALLER,
  '-device', 'ide-hd,bus=sata.3,drive=INSTALLER',
  '-drive', 'id=SYSTEM,format=qcow2,if=none,file=%s' % DISK_SYSTEM,
  '-device', 'ide-hd,bus=sata.4,drive=SYSTEM'
])
