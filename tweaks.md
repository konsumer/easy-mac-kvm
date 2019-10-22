## tweaking

There is lots you can do to tweak your setup to improve performance & usability.  I put everything for running stuff in [`run.py`](bin/run.py). Besides the tweaks listed here, feel free to modify your script however works for you (for example adding [bridged networking](https://ahelpme.com/linux/howto-do-qemu-full-virtualization-with-bridged-networking/))

### screen resolution

OSX resolution stays at whatever it boots from in UEFI, by default. You can change the boot-resolution by tweaking your [Clover](https://sourceforge.net/projects/cloverefiboot/) partition:

```
sudo apt-get install libguestfs-tools
# or sudo yum install libguestfs-tools

# create & mount & become root
mkdir mnt
sudo -s
guestmount -a disks/ESP.qcow2 -m /dev/sda1 mnt

# get current resolution
grep ScreenResolution -n1 mnt/EFI/CLOVER/config.plist

# set resolution via search & replace
sed -i s/1024x768/1920x1080/g mnt/EFI/CLOVER/config.plist

# clean up & exit root
umount mnt
rmdir mnt
exit
```

Do this when the VM isn't running.

Alternately, inside the VM, you can use [Clover Configurator](https://mackie100projects.altervista.org/download-clover-configurator/) to tweak all kinds of boot settings, including resolution, in a nice UI.


### increase RAM

You can use however much you can spare, by setting `SIZE_MEMORY` in [`run.py`](bin/run.py). On my 32GB system, I can safely set it to `24GB` without any problems on the host.

### more cpu cores

If you have a bunch of cores/threads, you should use them!

Find the part in [`run.py`](bin/run.py) that says `4,cores=2`, and change it to whatever you want. The first number needs to add up to the total number of thread/cores, when multiplied. I noticed on mac VMs, it seems to like lots of sockets, but less cores/threads. If it gets a toplogy it doesn't like, it will hang before it can boot. For example, I replaced `4,cores=2` with `64,sockets=16,cores=2,threads=2` on an [i7-8700](https://ark.intel.com/content/www/us/en/ark/products/126686/intel-core-i7-8700-processor-12m-cache-up-to-4-60-ghz.html). That means I give it 64 of my total 72 (6 cores * 12 threads), but it looks liek it has 26 dual-core CPU sockets. It's a bit counter-intuitive, but it's because OSX is happy with multiple sockets, but not thread/core combos it's not familiar with. I had to play around with different values until I got good performance + booting, but it was worth it (it's much faster than my macbook pro.)

### PCI passthrough

PCI passthrough lets your virtual-machines use video-hardware, directly. You will need an "extra" video card that gets passed through, in addition to your every day videocard. I use my onboard Intel video for day-to-day stuff, and passthrough an Nvidia Geforce GTX 1060. Your processor will also need to have IOMMU (VT-d on Intel, or newish AMD CPU.)

On my system, I have a seperate cable going from my monitor to the secondary card, and I switch inputs (via switch) on the monitor to see whats on the screen. It might make life easier to get a KVM switch like [this](https://www.amazon.com/gp/product/B07QM6ND7R/), so you can just swtich USB inputs & monitor all at once.

I am using [Pop!OS 19.10](https://system76.com/pop), so your system may (probably will) be different.

First, I added kernel-params:

```
sudo kernelstub -a "intel_iommu=on efifb=off"
```

Use this to get a list of devices:

```bash
lspci -vnn
```

The relevant parts of my setup are here:

```
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP106 [GeForce GTX 1060 6GB] [10de:1c03] (rev a1) (prog-if 00 [VGA controller])
	Subsystem: eVga.com. Corp. GP106 [GeForce GTX 1060 6GB] [3842:6163]
	Flags: fast devsel, IRQ 11
	Memory at a2000000 (32-bit, non-prefetchable) [disabled] [size=16M]
	Memory at 90000000 (64-bit, prefetchable) [disabled] [size=256M]
	Memory at a0000000 (64-bit, prefetchable) [disabled] [size=32M]
	I/O ports at 3000 [disabled] [size=128]
	Expansion ROM at a3000000 [disabled] [size=512K]
	Kernel modules: nvidiafb, nouveau

01:00.1 Audio device [0403]: NVIDIA Corporation GP106 High Definition Audio Controller [10de:10f1] (rev a1)
	Subsystem: eVga.com. Corp. GP106 High Definition Audio Controller [3842:6163]
	Flags: bus master, fast devsel, latency 0, IRQ 10
	Memory at a3080000 (32-bit, non-prefetchable) [size=16K]
	Kernel modules: snd_hda_intel
```

So I will use `01:00.0` & `01:00.1` (prefixed with `0000:`):

```bash
sudo -s
echo '#!/bin/sh
PREREQS=""
DEVS="0000:01:00.0 0000:01:00.1"
for DEV in $DEVS;
  do echo "vfio-pci" > /sys/bus/pci/devices/$DEV/driver_override
done
modprobe -i vfio-pci' > /etc/initramfs-tools/scripts/init-top/bind_vfio.sh

chmod 755 /etc/initramfs-tools/scripts/init-top/bind_vfio.sh
echo 'vfio-pci' >> /etc/initramfs-tools/modules
update-initramfs -u
```

At this point, reboot for the changes to take effect.

Check to make sure it worked:

```bash
lspci -vnn
```

```
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP106 [GeForce GTX 1060 6GB] [10de:1c03] (rev a1) (prog-if 00 [VGA controller])
	Subsystem: eVga.com. Corp. GP106 [GeForce GTX 1060 6GB] [3842:6163]
	Flags: fast devsel, IRQ 11
	Memory at a2000000 (32-bit, non-prefetchable) [disabled] [size=16M]
	Memory at 90000000 (64-bit, prefetchable) [disabled] [size=256M]
	Memory at a0000000 (64-bit, prefetchable) [disabled] [size=32M]
	I/O ports at 3000 [disabled] [size=128]
	Expansion ROM at a3000000 [disabled] [size=512K]
	Capabilities: <access denied>
	Kernel driver in use: vfio-pci
	Kernel modules: nvidiafb, nouveau

01:00.1 Audio device [0403]: NVIDIA Corporation GP106 High Definition Audio Controller [10de:10f1] (rev a1)
	Subsystem: eVga.com. Corp. GP106 High Definition Audio Controller [3842:6163]
	Flags: bus master, fast devsel, latency 0, IRQ 10
	Memory at a3080000 (32-bit, non-prefetchable) [size=16K]
	Capabilities: <access denied>
	Kernel driver in use: vfio-pci
	Kernel modules: snd_hda_intel
```

The good part is `Kernel driver in use: vfio-pci`.


#### attach card to QEMU

Finally, you will need to add lines to [`run.py`](bin/run.py) to tell your vmachine about the PCI devices & disable built-in VGA, again using the output of above `lspci`. Set `ROM_VIDEO` to the path of a file you downloaded from [video bios database](https://www.techpowerup.com/vgabios/).

```py
run([
  'qemu-system-x86_64',
  '-enable-kvm',
  '-m', SIZE_MEMORY,
  '-machine', 'q35,accel=kvm',
  '-smp', '4,cores=2',
  '-cpu', 'Penryn,vendor=GenuineIntel,kvm=on,+sse3,+sse4.2,+aes,+xsave,+avx,+xsaveopt,+xsavec,+xgetbv1,+avx2,+bmi2,+smep,+bmi1,+fma,+movbe,+invtsc',
  '-device', 'isa-applesmc,osk=ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc',
  '-smbios', 'type=2',
  '-drive', 'if=pflash,format=raw,readonly,file=%s' % OVM_CODE,
  '-drive', 'if=pflash,format=raw,file=%s' % OVM_VARS,
  '-device', 'ich9-intel-hda',
  '-device', 'hda-output',
  '-usb',
  '-device', 'usb-kbd',
  '-device', 'usb-mouse',
  '-netdev', 'user,id=net0',
  '-device', 'e1000-82545em,netdev=net0,id=net0,mac=%s' % MAC_ADDRESS,
  '-device', 'ich9-ahci,id=sata',
  '-drive', 'id=ESP,if=none,format=qcow2,file=%s' % DISK_ESP,
  '-device', 'ide-hd,bus=sata.2,drive=ESP',
  '-drive', 'id=SYSTEM,format=qcow2,if=none,file=%s' % DISK_SYSTEM,
  '-device', 'ide-hd,bus=sata.4,drive=SYSTEM',
  '-vga', 'none',
  '-device', 'pcie-root-port,bus=pcie.0,multifunction=on,port=1,chassis=1,id=port.1',
  '-device', 'vfio-pci,host=01:00.0,multifunction=on,romfile=%s' % ROM_VIDEO,
  '-device', 'vfio-pci,host=01:00.1'
])
```

#### evdev

I wanted to be able to swap input with keyboard/mouse, directly (rather than interact with the vmachine through the qemu graphic window) so I use evdev. I followed the advice [here](https://passthroughpo.st/using-evdev-passthrough-seamless-vm-input/) to set it up. It takes a few steps, and might not be worth it if you have a KVM switch like [this](https://www.amazon.com/gp/product/B07QM6ND7R/) laying around.

#### libvirt

[libvirt](https://libvirt.org/) is a high-level wrapper around other virtualization tech, like qemu, as we are using here. It has a nice GUI called [virt-manager](https://virt-manager.org/). It seems to screw up advanced stuff like qemu params for optimizing CPU and sound, so I stopped using it personally, but I included it anyway, in case you want to use it. `virsh edit MACHINE` is totally safe, but I saw little reason to use it, once my qemu script was dialed in. Before you run it, tweak the script to your taste (should closely match [`run.py`](bin/run.py).)

```bash
./bin/virt.py
virsh define ./libvirt-10.15.xml
virt-manager
```
