+++
title = "Getting Started"
slug = "GettingStarted"
url = "/Using/GettingStarted/"
weight = -50
+++

Bcachefs is not yet upstream - you'll have to [build a kernel](https://kernelnewbies.org/KernelBuild) to use it.

First, check out the bcachefs kernel and tools repositories:

```shell
git clone https://evilpiepirate.org/git/bcachefs.git
git clone https://evilpiepirate.org/git/bcachefs-tools.git
```

Build and install as usual - make sure you enable `CONFIG_BCACHEFS_FS`. Then, to
format and mount a single device with the default options, run:

```shell
bcachefs format /dev/sda1
mount -t bcachefs /dev/sda1 /mnt
```

For a multi device filesystem, with sda1 caching sdb1:

```shell
bcachefs format /dev/sd[ab]1 \
    --foreground_target /dev/sda1 \
    --promote_target /dev/sda1 \
    --background_target /dev/sdb1
mount -t bcachefs /dev/sda1:/dev/sdb1 /mnt
```

This will configure the filesystem so that writes will be buffered to /dev/sda1
before being written back to /dev/sdb1 in the background, and that hot data
will be promoted to /dev/sda1 for faster access.

See `bcachefs format --help` for more options.
