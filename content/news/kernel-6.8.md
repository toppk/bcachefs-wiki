+++
title = "Linux 6.8: bcachefs merges"
date = 2024-02-25T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.8.

## RC1

- **2024-01-10**: Merge tag 'bcachefs-2024-01-10' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/999a36b52b1b11b2ca0590756e4f8cf21f2d9182))
  <details open>
  <summary>Show full message</summary>

  ```text
  Pull bcachefs updates from Kent Overstreet:
  
   - btree write buffer rewrite: instead of adding keys to the btree write
     buffer at transaction commit time, we now journal them with a
     different journal entry type and copy them from the journal to the
     write buffer just prior to journal write.
  
     This reduces the number of atomic operations on shared cachelines in
     the transaction commit path and is a signicant performance
     improvement on some workloads: multithreaded 4k random writes went
     from ~650k iops to ~850k iops.
  
   - Bring back optimistic spinning for six locks: the new implementation
     doesn't use osq locks; instead we add to the lock waitlist as normal,
     and then spin on the lock_acquired bit in the waitlist entry, _not_
     the lock itself.
  
   - New ioctls:
  
      - BCH_IOCTL_DEV_USAGE_V2, which allows for new data types
  
      - BCH_IOCTL_OFFLINE_FSCK, which runs the kernel implementation of
        fsck but without mounting: useful for transparently using the
        kernel version of fsck from 'bcachefs fsck' when the kernel
        version is a better match for the on disk filesystem.
  
      - BCH_IOCTL_ONLINE_FSCK: online fsck. Not all passes are supported
        yet, but the passes that are supported are fully featured - errors
        may be corrected as normal.
  
     The new ioctls use the new 'thread_with_file' abstraction for kicking
     off a kthread that's tied to a file descriptor returned to userspace
     via the ioctl.
  
   - btree_paths within a btree_trans are now dynamically growable,
     instead of being limited to 64. This is important for the
     check_directory_structure phase of fsck, and also fixes some issues
     we were having with btree path overflow in the reflink btree.
  
   - Trigger refactoring; prep work for the upcoming disk space accounting
     rewrite
  
   - Numerous bugfixes :)
  
  * tag 'bcachefs-2024-01-10' of https://evilpiepirate.org/git/bcachefs: (226 commits)
    bcachefs: eytzinger0_find() search should be const
    bcachefs: move "ptrs not changing" optimization to bch2_trigger_extent()
    bcachefs: fix simulateously upgrading & downgrading
    bcachefs: Restart recovery passes more reliably
    bcachefs: bch2_dump_bset() doesn't choke on u64s == 0
    bcachefs: improve checksum error messages
    bcachefs: improve validate_bset_keys()
    bcachefs: print sb magic when relevant
    bcachefs: __bch2_sb_field_to_text()
    bcachefs: %pg is banished
    bcachefs: Improve would_deadlock trace event
    bcachefs: fsck_err()s don't need to manually check c->sb.version anymore
    bcachefs: Upgrades now specify errors to fix, like downgrades
    bcachefs: no thread_with_file in userspace
    bcachefs: Don't autofix errors we can't fix
    bcachefs: add missing bch2_latency_acct() call
    bcachefs: increase max_active on io_complete_wq
    bcachefs: add time_stats for btree_node_read_done()
    bcachefs: don't clear accessed bit in btree node fill
    bcachefs: Add an option to control btree node prefetching
    ...
  ```
  </details>

- **2024-01-21**: Merge tag 'bcachefs-2024-01-21' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/35a4474b5c3dd4315f72bd53e87b97f128d9bb3d))
  <details>
  <summary>Show full message</summary>

  ```text
  Pull more bcachefs updates from Kent Overstreet:
   "Some fixes, Some refactoring, some minor features:
  
     - Assorted prep work for disk space accounting rewrite
  
     - BTREE_TRIGGER_ATOMIC: after combining our trigger callbacks, this
       makes our trigger context more explicit
  
     - A few fixes to avoid excessive transaction restarts on
       multithreaded workloads: fstests (in addition to ktest tests) are
       now checking slowpath counters, and that's shaking out a few bugs
  
     - Assorted tracepoint improvements
  
     - Starting to break up bcachefs_format.h and move on disk types so
       they're with the code they belong to; this will make room to start
       documenting the on disk format better.
  
     - A few minor fixes"
  
  * tag 'bcachefs-2024-01-21' of https://evilpiepirate.org/git/bcachefs: (46 commits)
    bcachefs: Improve inode_to_text()
    bcachefs: logged_ops_format.h
    bcachefs: reflink_format.h
    bcachefs; extents_format.h
    bcachefs: ec_format.h
    bcachefs: subvolume_format.h
    bcachefs: snapshot_format.h
    bcachefs: alloc_background_format.h
    bcachefs: xattr_format.h
    bcachefs: dirent_format.h
    bcachefs: inode_format.h
    bcachefs; quota_format.h
    bcachefs: sb-counters_format.h
    bcachefs: counters.c -> sb-counters.c
    bcachefs: comment bch_subvolume
    bcachefs: bch_snapshot::btime
    bcachefs: add missing __GFP_NOWARN
    bcachefs: opts->compression can now also be applied in the background
    bcachefs: Prep work for variable size btree node buffers
    bcachefs: grab s_umount only if snapshotting
    ...
  ```
  </details>

## RC2

- **2024-01-27**: Merge tag 'bcachefs-2024-01-26' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/064a4a5bfac8bb24af08ec8a4c2664ff61a06f16))
  <details>
  <summary>Show full message</summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
  
   - fix for REQ_OP_FLUSH usage; this fixes filesystems going read only
     with -EOPNOTSUPP from the block layer.
  
     (this really should have gone in with the block layer patch causing
     the -EOPNOTSUPP, or should have gone in before).
  
   - fix an allocation in non-sleepable context
  
   - fix one source of srcu lock latency, on devices with terrible discard
     latency
  
   - fix a reattach_inode() issue in fsck
  
  * tag 'bcachefs-2024-01-26' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: __lookup_dirent() works in snapshot, not subvol
    bcachefs: discard path uses unlock_long()
    bcachefs: fix incorrect usage of REQ_OP_FLUSH
    bcachefs: Add gfp flags param to bch2_prt_task_backtrace()
  ```
  </details>

## RC4

- **2024-02-06**: Merge tag 'bcachefs-2024-02-05' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/99bd3cb0d12e85d5114425353552121ec8f93adc))
  <details>
  <summary>Show full message</summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Two serious ones here that we'll want to backport to stable: a fix for
    a race in the thread_with_file code, and another locking fixup in the
    subvolume deletion path"
  
  * tag 'bcachefs-2024-02-05' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: time_stats: Check for last_event == 0 when updating freq stats
    bcachefs: install fd later to avoid race with close
    bcachefs: unlock parent dir if entry is not found in subvolume deletion
    bcachefs: Fix build on parisc by avoiding __multi3()
  ```
  </details>

## RC5

- **2024-02-17**: Merge tag 'bcachefs-2024-02-17' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/f2667e0c32404a68496891b2d2015825de189b06))
  <details>
  <summary>Show full message</summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Mostly pretty trivial, the user visible ones are:
  
     - don't barf when replicas_required > replicas
  
     - fix check_version_upgrade() so it doesn't do something nonsensical
       when we're downgrading"
  
  * tag 'bcachefs-2024-02-17' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: Fix missing va_end()
    bcachefs: Fix check_version_upgrade()
    bcachefs: Clamp replicas_required to replicas
    bcachefs: fix missing endiannes conversion in sb_members
    bcachefs: fix kmemleak in __bch2_read_super error handling path
    bcachefs: Fix missing bch2_err_class() calls
  ```
  </details>

## RC6

- **2024-02-25**: Merge tag 'bcachefs-2024-02-25' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/e231dbd452a79b9100846c0552fd9077251c042e))
  <details>
  <summary>Show full message</summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Some more mostly boring fixes, but some not
  
    User reported ones:
  
     - the BTREE_ITER_FILTER_SNAPSHOTS one fixes a really nasty
       performance bug; user reported an untar initially taking two
       seconds and then ~2 minutes
  
     - kill a __GFP_NOFAIL in the buffered read path; this was a leftover
       from the trickier fix to kill __GFP_NOFAIL in readahead, where we
       can't return errors (and have to silently truncate the read
       ourselves).
  
       bcachefs can't use GFP_NOFAIL for folio state unlike iomap based
       filesystems because our folio state is just barely too big, 2MB
       hugepages cause us to exceed the 2 page threshhold for GFP_NOFAIL.
  
       additionally, the flags argument was just buggy, we weren't
       supplying GFP_KERNEL previously (!)"
  
  * tag 'bcachefs-2024-02-25' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: fix bch2_save_backtrace()
    bcachefs: Fix check_snapshot() memcpy
    bcachefs: Fix bch2_journal_flush_device_pins()
    bcachefs: fix iov_iter count underflow on sub-block dio read
    bcachefs: Fix BTREE_ITER_FILTER_SNAPSHOTS on inodes btree
    bcachefs: Kill __GFP_NOFAIL in buffered read path
    bcachefs: fix backpointer_to_text() when dev does not exist
  ```
  </details>
