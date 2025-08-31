+++
title = "Bcachefs"
+++

## "The COW filesystem for Linux that won't eat your data"

Bcachefs is an advanced new filesystem for Linux, with an emphasis on reliability and robustness and the complete set of features one would expect from a modern filesystem.

* Copy on write (COW) - like zfs
* Full data and metadata checksumming, for full data integrity: the filesystem should always detect (and where possible, recover from) damage; it should never return incorrect data.
* Multiple devices
* Replication
* [Erasure coding](/Features/ErasureCoding/) (incomplete)
  High performance: doesn't fragment your writes (like ZFS), no RAID hole
* [Caching & Data Placement](/Features/CachingAndDataPlacement/)
* [Compression](/Features/Compression/)
* [Encryption](/Features/Encryption/)
* [Snapshots](/Features/Snapshots/)
* Nocow mode
* Reflink
* Extended attributes, ACLs, quotas
* Petabyte scalability
* Full online fsck, check and repair (in progress)
* Robustness and rock solid repair. Damage and breakage are a fact of life, it's not a matter of if, but when. It doesn't matter what happened to the filesystem: bad hardware, lightning strikes, an errant dd, you can expect that bcachefs will repair the damage and keep going, usually with no user intervention required.

  It's the job of the filesystem to never lose your data: anything that can be repaired, will be.
