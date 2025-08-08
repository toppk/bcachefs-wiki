+++
title = "Roadmap for future work"
slug = "Roadmap"
url = "/Developer/Roadmap/"
+++


## More ways of setting IO path options

We need an option for setting IO path options on a per file descriptor or per
process basis.

## tmpdir support

Add a directory option for using it as a tmpdir - the contents will be deleted
on every mount.

Since the contents won't be needed after an unclean shutdown, there's no need
for fsync() to do anything - this option will also turn fsync() into a noop,
and without the fsync buffered IO will only be flushed on memory reclaim -
meaning, tmpdir directories should perform just as well as a tmpfs.

## Compression

We'd like to add multithreaded compression, for when a single thread is doing
writes at a high enough rate to be CPU bound.

We'd also like to add support for xz compression: this will be useful when
doing a "squashfs-like" mode. The blocker is that kernel only has support for
xz decompression, not compression - hopefully we can get this added.

## Scrub

We're still missing scrub support. Scrub's job will be to walk all data in the
filesystem and verify checksums, recovery bad data from a good copy if it
exists or notifying the user if data is unrecoverable.

Since we now have backpointers, we have the option of doing scrub in keyspace
order, or lba order - lba order will be much better for rotational devices.

## Configurationless tiered storage

We're starting to work on benchmarking individual devices at format time, and
storing their performance characteristics in the superblock.

This will allow for a number of useful things - including better tracking of
drive health over time - but the real prize will be tiering that doesn't
require explicit configuration: foreground writes will preferentially go to
the fastest device(s), and in the background data will be moved from fast
devices to slow devices, taking into account how hot or cold that data is.

Even better, this will finally give us a way to manage more than two tiers, or
performance classes, of devices.

## Disk space accounting

Currently, disk space accounting is primarily persisted in the journal (on
clean shutdown, it's also stored in the superblock), and each disk space
counter is added to every journal entry.

So currently there's a real limit on how many counters we can maintain, and
we'll need to do something else before adding e.g. per snapshot disk space
accounting.

We'll need to make disk space accounting keys in a btree, like all other
metadata. Since disk space accounting was implemented we've gained the btree
write buffer code, so this is now possible: on transaction commit, we will do
write buffer updates with deltas for the counters being modified, and then the
btree write buffer flush code will handle summing up the deltas and flushing
the updates to the underlying btree.

We also want to add more counters to the inode. Right now in the inode we only
track sectors used as fallocate would see them - we should add counters that
take into account replication and compression.

### Device management

We need a concept of "failure domains", and perhaps something more, for managing
large numbers of devices with bcachefs to make sense. Currently, disks can be
assigned labels that are essentially paths, delimited by periods, e.g.

  controller1.ssd.ssd1
  controller1.ssd.ssd2
  controller1.hdd.hdd1
  controller2.hdd.hdd1
  controller2.hdd.hdd2

This lets disks be organized into a heirarchy, and referring to any part of the
heirarchy will include all the disks underneath that point: e.g. controller1
would refer to the first three disks in the example.

This is insufficient, though. If a user has a filesystem with 60 drives, all
alike, we need a way to specify that some disks are on the same controller and
that multiple replicas should not be stored on the same controller, and we also
need a way to constrain how replicated writes are laid out. Today, in a 60
devices filesystem with 3x replication, each allocation will be unconstrained
which means that the failure of _any_ three devices would lead to loss of data.

A feature that addresses these issues still needs to be designed.

### Send and receive

Like ZFS and btrfs have, we need it to. This will give us the ability to
efficiently synchronize filesystems over a network for backup/redundancy
purposes - much more efficient than rsync, and it'll pair well with snapshots.

Since all metadata exists as btree keys, this won't be a huge amount of work
to implement: we need a network protocol, and then we need to scan and send
for keys newer than version number X (if making use of key version numbers),
or keys newer than a given snapshot ID.

### Support for sub-block size writes

Devices with larger than 4k blocksize are coming, and this is going to result
in more wasted disk space due to internal fragmentation.

Support for writes at smaller than blocksize granularity would be a useful
addition. The read size is easy: they'll require bouncing, which we already
support. Writes are trickier - there's a few options:

* Buffer up writes when we don't have full blocks to write? Highly
   problematic, not going to do this.
* Read modify write? Not an option for raw flash, would prefer it to not be
   our only option
* Do data journalling when we don't have a full block to write? Possible
   solution, we want data journalling anyways

### Journal on NVRAM devices

NVRAM devices are currently a specialized thing, which are always promising to
become more widely available. We could make use of them for the journal;
they'd let us cheaply add full data journalling (useful for previous feature)
and greatly reduce fsync overhead.

### Online fsck

For supporting huge filesystems, and competing with XFS, we will eventually
need online fsck.

This will be easier in bcachefs than it was in XFS, since our fsck
implementation is part of the main filesystem codebase and uses the normal
btree transaction API that's available at runtime.

That means that the current fsck implementation will eventually also be the
online fsck implementation: the process will mostly be a matter of auditing the
existing fsck codebase for locking issues, and adding additional locking w.r.t.
the rest of the filesystem where needed.

## ZNS, SMR device support

[ZNS](https://zonedstorage.io/docs/introduction/zns) is a technology for
cutting out the normal normal flash translation layer (FTL), and instead
exposing an interface closer to the raw flash.

SSDs have large erase units, much larger than the write blocksize, so the FTL
has to implement a mapping layer as well as garbage collection to expose a
normal, random write block device interface. Since a copy-on-write filesystem
needs both of these anyways, adding ZNS support to bcachefs will eliminate a
significant amount of overhead and improve performance, especially tail latency.

[SMR](https://en.wikipedia.org/wiki/Shingled_magnetic_recording) is another
technology for rotational hard drives, completely different from ZNS in
implementation but quite similar in how it is exposed and used. SMR enables
higher density, and supporting it directly in the filesystem eliminates much of
the performance penalties.

bcachefs allocation is bucket based: we allocate an entire bucket, write to it
once, and then never rewrite it until the entire bucket is empty and ready to
be reused. This maps nicely to both ZNS and SMR zones, which makes supporting
both of these directly particularly attractive.

## Squashfs mode

Righ now we have dedicated filesystems, like
[squashfs](https://en.wikipedia.org/wiki/SquashFS), for building and reading
from a highly compressed but read-only filesystem.

bcachefs metadata is highly space efficient (e.g. [packed
bkeys](https://bcachefs.org/Architecture/#Bkey_packing) ), and could probably
serve as a direct replacement with a relatively small amount of work to
generate a filesystem image in the most compact way. The same filesystem image
could later be mounted read-write, if given more space.

Specifying a directory tree to include when creating a new filesystem is
already a requested feature - other filesystems have this as the `-c` option
to mkfs.

## Container filesystem mode

Container filesystems are another special purpose type of filesystem we could
potentially fold into bcachefs - e.g.
[puzzlefs](https://github.com/project-machine/puzzlefs)

These have a number of features, e.g. verity support for cryptographically
verifying a filesystem image (which we can do via our existing cryptographic
MAC support) - but the interesting feature here is support for referring to
data (extents, entire files) in a separate location - in this case, the host
filesystem.

### Cloud storage management

The previous feature is potentially more widely useful: allowing inodes and
extents to refer to arbitrary callbacks for fetching/storing data would be the
basis for managing data in e.g. cloud storage, and in combination with local
storage in a seamless tierid system.
