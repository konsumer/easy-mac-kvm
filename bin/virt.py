#!/usr/bin/env python

""" Create a libvirt vmachine """

from fetch import *
from uuid import uuid4

VERSION='10.15'
DIR_DISKS=os.path.realpath('./disks')
DIR_OVM=os.path.realpath('./firmware')
OUT_FILE=os.path.realpath('./libvirt-%s.xml' % (VERSION))

DISK_SYSTEM='%s/System-%s.qcow2' % (DIR_DISKS, VERSION)
DISK_ESP='%s/ESP.qcow2' % DIR_DISKS
OVM_CODE='%s/OVMF_CODE.fd' % DIR_OVM
OVM_VARS='%s/OVMF_VARS.fd' % DIR_OVM

# openssl rand -hex 6 | sed 's/\(..\)/\1:/g; s/.$//'
MAC_ADDRESS='a0:9f:de:46:89:2b'

# in kB
SIZE_MEMORY=2 * 1024 * 1024

# CPU topology
CPU_TOTAL=4
SOCKETS=1
CORES=2
THREADS=2

template = open(os.path.dirname(os.path.realpath(__file__)) + '/template-libvirt.xml').read()
template = template.replace('VERSION', VERSION)
template = template.replace('DISK_SYSTEM', DISK_SYSTEM)
template = template.replace('DISK_ESP', DISK_ESP)
template = template.replace('OVM_CODE', OVM_CODE)
template = template.replace('OVM_VARS', OVM_VARS)
template = template.replace('MAC_ADDRESS', MAC_ADDRESS)
template = template.replace('CPU_TOTAL', '%d' % CPU_TOTAL)
template = template.replace('SOCKETS', '%d' % SOCKETS)
template = template.replace('CORES', '%d' % CORES)
template = template.replace('THREADS', '%d' % THREADS)
template = template.replace('UUID', str(uuid4()))
template = template.replace('SIZE_MEMORY', '%d' % SIZE_MEMORY)

f=open(OUT_FILE, 'w')
f.write(template)
f.close()