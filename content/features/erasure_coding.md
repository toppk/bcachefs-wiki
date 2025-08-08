+++
title = "Erasure Coding"
slug = "ErasureCoding"
url = "/Features/ErasureCoding/"
+++


The term erasure coding refers to the mathematical algorithms for adding
redundancy to data that allows errors to be corrected: see
[https://en.wikipedia.org/wiki/Erasure_code](https://en.wikipedia.org/wiki/Erasure_code).

Bcachefs, like most RAID implementations, currently supports Reed-Solomon. We
might add support for other algorithms in the future, but Reed-Solomon has the
nice property can always correct up to n errors in a stripe given n redundant
blocks - no erasure coding algorithm can do better than this. The disadvantage
of Reed-Solomon is that it always has to read every block within a stripe to fix
errors - this means that large stripes lead to very slow rebuild times. It might
be worth investigating other algorithms, like
[weaver codes](https://www.usenix.org/legacy/events/fast05/tech/full_papers/hafner_weaver/hafner_weaver.pdf) in the future.

## Limitations of other implementions

Conventional software raid suffers from the "raid hole": when writing to a
single block within a stripe, we have to update the p/q blocks as well. But the
writes of the p/q blocks are not atomic with the data block write - and can't be
atomic since they're on different disks (not without e.g. a battery backed up
journal, as some hardware raid controllers have). This means that there is a
window of time where the p/q blocks will be inconsistent with the data blocks,
and if we crash during this window and have to rebuild because one of our drives
didn't come back, we will rebuild incorrect data (and crucially, we will rebuild
incorrect data for blocks within the stripe that weren't being written to).

Any software raid implementation that updates existing stripes without doing
full data journalling is going to suffer from this issue - btrfs is still
affected by the RAID hole.

ZFS avoids this issue by turning every write into a full stripe - this means
they never have to update an existing stripe in place. The downside is that
every write is fragmented across every drive in the RAID set, and this is really
bad for performance with rotating disks (and even with flash it's not ideal).
Read performance on rotating disks is dominated by seek time, and fragmenting
reads means instead of doing one seek we're now doing n seeks, where n is the
number of disks in the raid set (minus redundancy).

## Erasure coding in bcachefs

Bcachefs takes advantage of the fact that it is already a copy on write
filesystem. If we're designing our filesystem to avoid update-in-place, why
would we do update-in-place in our RAID implementation?

We're able to do this because additionally allocation is bucket based. We divide
our storage devices up into buckets - typically 512k-2M. When we allocate a
bucket, we write to it sequentially and then we never overwrite it until the
entire bucket has been evacuated (or invalidated, if it contained cached data).

Erasure coding in bcachefs works by creating stripes of buckets, one per device.
Foreground writes are initially replicated, but when erasure coding is enabled
one of the replicas will be allocated from a bucket in a stripe being newly
created. When all the data buckets within the new stripe have been written, we
write out our p/q buckets, then update all the data pointers into that stripe to
drop their extra replicas and add a reference to the stripe. Buckets within that
stripe will never be overwritten until the stripe becomes empty and is released.

This has a number of advantages:

- No RAID hole
- Erasure coding doesn't affect data layout - it doesn't cause writes to be
   fragmented. Data layout is the same as it would be with no replication or
   erasure coding.
- Since we never update existing stripes, and stripe creation is done once all
   the data buckets within the stripe are written, the code is vastly simpler
   and easier to test than other implementations (e.g. Linux md raid5/6).

Disadvantages:

- Nontrivial interactions with the copying garbage collector.
