# easy mac kvm

This will help you setup a mac KVM very quickly.

To use it, you will need python & qemu installed, and kvm only works on Linux.

```bash
# download image, and start qemu VM to setup OSX
python bin/setup.py

# run your VM
python bin/run.py
```

If you just want to download an IMG file for use in qemu:

```bash
python bin/fetch.py --osx 10.15 myinstaller.img
```

## thanks

These 2 projects gave me lots of great ideas:

* [OSX-KVM](https://github.com/kholia/OSX-KVM/)
* [macOS-Simple-KVM](https://github.com/foxlet/macOS-Simple-KVM/)