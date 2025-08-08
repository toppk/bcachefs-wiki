+++
title = "Introduction"
slug = "Introduction"
url = "/Using/Introduction/"
weight = -100
+++
## About

There are two main themes or ideas that make up bcachefs: copy on write, and filesystem-as-database. These are the two primary tools for achieving reliability: a filesystem that won't corrupt or lose your data, and that can always be repaired even when things go horribly wrong.

### History - ZFS

The history of modern filesystems starts with ZFS. Their primary goal was a filesystem that absolutely guarantees data integrity, and COW is primary mechanism by which ZFS achieves that goal: it enables full data and metadata checksumming, with a chain of trust up to a single root, the superblock.

This came out of real world experience with failure modes of block storage that conventional filesystems weren't able to protect against: bit corruption, lost writes, misdirected writes, and others. COW, coupled with full data and metadata checksumming, makes it possible for the filesystem to definitively guard against all of them: a properly implemented COW filesystem should never return incorrect data.

The push towards copy on write goes back even further in academic research. It had long been realized that it was fundamentally a safer technique than update-in-place, but ZFS was the first to realize COW in a filesystem and demonstrate the benefits to data integrity.

### Filesystem as a database

The other half of bcachefs is "filesystem as a database".

The original Unix filesystem (and other filesystems of the era are broadly similar in concept, though the ideas were different) was implemented with various special purpose (but simple - originally) on disk data structures: inodes (file metadata) of fixed size that live in fixed locations on disk, file data stored in blocks (not extents) indexed by radix trees hanging off the inode, and simple bitmaps for free space allocation.

This worked well when filesystems were 1k loc, or 10k loc. But every additional feature needed new on disk data structures and pushed the limits of this design, with transactional correctness (filesystems that don't need a fsck after a crash) being a particularly big jump in complexity. In this model, every additional feature has needed new on disk data structures - each unique and special purpose. High performance directory indexing, xattrs, reflink, and a great many features not visible to users but necessary for scalability to modern filesystem sizes.

Notably, ZFS has more in common with the original Unix filesystem in the design of its data structures than other modern filesystems, for what were good and pragmatic reasons at the time. Their primary goal was robustness, and that has been the strength of filesystems in that lineage (as with ext2/3/4, also based off the original Unix filesystem): those simple, often fixed-location on disk data structures make for reliable repair.

But as research into b-trees and databases advanced, a great many filesystems looked at that and said: "Wouldn't life be simpler if all metadata was just keys in a key/value store?", with that ideally being a single core b-tree/database implementation, with scalability and performance usually being primary goals.

XFS was the earliest and most successful of the "everything is a b-tree" approach, but largely predating the push towards COW filesystems, and didn't push the "unified data model" very far in comparison to later filesystems. Reiserfs and btrfs are also notable for pushing this approach.

Historically, the primary disadvantages of this approach has been:

* Robustness. "Everything is a b-tree" introduces new single points of failure (b-tree roots), and high performance, production quality b-trees are notoriously complicated beasts.
* Performance. The original Unix filesystem design had a major scalability advantage, with a lot of built in sharding at the inode level. Fully realizing the benefits of the "filesystem as a database" approach requires tossing that out: instead of many b-trees, one per inode, having internals that work like a normal-ish database requires the filesystem to be implemented with a few massive b-trees: then we can have something that starts to look like a relational database, with tables corresponding to data types, and simple unified transactional interface.

These have been the achille's heels, and the reason why other more modern COW filesystems have not lived up to ZFS's robustness.

### History of bcachefs, and how these were solved

Enter bcache, the prototype for bcachefs. When SSDs were first being introduced, they were from the beginning orders of magnitude faster than rotating disk - but expensive, so block layer caching was an obvious approach for using them effectively.

Whereas other approaches towards SSD caching at the time were based on hash tables (which have major disadvantages as persistent data structures, and don't support range lookups - making indexing extents instead of blocks extremely problematic), bcache went with a b-tree approach, with several novel innovations to make the b-tree performant enough to work for indexing every IO lookup, without sharding. The primary innovation was log structured btree nodes: this enabled eytzinger search trees, which eliminates binary search. This was huge: binary search is O(log n), but from a CPU cache perspective is the worst lookup algorithm possible.

This made bcache's b-tree one of the fastest ordered, persistent, production-quality key value stores around; more importantly, making the rest of the problems in "modern COW filesystem with real database underpinnings" tractable.

### Robustness and reliability: making "restore from backup" a thing of the past

Unlike the rest, there is no silver bullet to producing truly reliable code. Reliability comes from making it a priority and sticking to it, at every stage of development; learning from every accident and mistake, discovering all the failure modes that can happen in the wild, and continually building on those lessons and experience.

Some approaches pioneered in other filesystems:

* btree node scan, for disaster recovery scenarios - originally done in reiserfs. The reiserfs implementation had issues; notably, it would pick up btree nodes from unrelated filesystems on the same device. bcachefs corrects all of these with improved per-btree-node metadata, and makes it practical for the huge filesystems of today by segregating data and metadata (and noting which regions are which in the superblock).
* Extensive runtime verification of metadata, any time metadata is read - or written; XFS also makes heavy use of this approach. This drastically reduces the impact of bugs: bugs that would otherwise result in filesystem corruption typically result in emergency shutdown - restart and keep going, and bugs are caught much more quickly (and are therefore much easier to debug).
* Full filesystem rollback, as in log structured filesystems (like nilfs2), and ZFS in limited fashion. This falls out of the "filesystem as a database" approach: with all metadata as keys in b-trees, with all updates (and overwrites) logged in a single unified journal, anything can be rolled back.

Other areas of emphasis:

* Comprehensive and thorough logging, introspection, and debugging tools.
  
  You can't debug what you can't see. Any time something goes wrong, the system should tell you clearly what went wrong, and tell you clearly and directly everything you, as an end user or engineer, need to understand what went wrong and debug the issue.
* Comprehensive and robust fsck
  
  Notably, filesystem repair is considerably simplified with the "filesystem as a database" approach, but it's still a major topic, worth its own chapter in the user manual.
  
  The main point is: repair is not, and cannot be, an afterthought. It doesn't matter what the cause of the damage was, it's the filesystem's job to repair it, without causing additional damage or loss.

If you're running bcachefs: you won't lose data. If you find a way to break it: first, I'll be impressed, and secondly - get in contact. We've got the debugging tools to make short work of anything that may come up, and real world testing (the crazier, the better!) is how we make this filesystem more robust and rock solid for everyone.

### A few other things worth mentioning

#### Unified codebase

The entire bcachefs codebase can be built and used either inside the kernel, or in userspace - notably, fsck is not a from-scratch implementation, it's just a small module in the larger bcachefs codebase.

#### Rust

We've got some initial work done on transitioning to Rust, with plans for much more: here's an example of walking the btree, from Rust: [cmd_list](https://evilpiepirate.org/git/bcachefs-tools.git/tree/src/commands/list.rs)
