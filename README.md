# easy mac kvm

This will help you setup a mac KVM very quickly & easily. If you generate your basic setup and run the [tweaks](./tweaks.md), you should get near-native speed (which is faster than a real Mac, on new processors & video cards.)

To use it, you will need python & qemu installed, and kvm only works on a Linux host. You will also need harware-virtualization on your processor.

If you haven't already, install qemu:

```bash
sudo apt install qemu-system
```

```bash
# get the files
git clone --depth=1 https://github.com/konsumer/easy-mac-kvm.git mymac
cd mymac

# download image, and start qemu VM to setup Catalina OSX, by default
./bin/setup.py

# run your VM
./bin/run.py
```

If you just want to download an installer IMG file for use in your own qemu scripts:

```bash
./bin/fetch.py --osx 10.15 myinstaller.img
```

## thanks

These things gave me lots of great ideas & inspiration:

* [OSX-KVM](https://github.com/kholia/OSX-KVM/)
* [macOS-Simple-KVM](https://github.com/foxlet/macOS-Simple-KVM/)
* [VFIO reddit](https://www.reddit.com/r/VFIO/)
* [Hackintosh reddit](https://www.reddit.com/r/hackintosh/)
