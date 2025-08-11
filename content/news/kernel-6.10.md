+++
title = "Linux 6.10: bcachefs merges"
date = 2024-07-12T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.10.

## RC1

- **2024-05-19**: Merge tag 'bcachefs-2024-05-19' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/16dbfae867cdeb32f3d24cea81193793d5decc61))
  <details open>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs updates from Kent Overstreet:
  
   - More safety fixes, primarily found by syzbot
  
   - Run the upgrade/downgrade paths in nochnages mode. Nochanges mode is
     primarily for testing fsck/recovery in dry run mode, so it shouldn't
     change anything besides disabling writes and holding dirty metadata
     in memory.
  
     The idea here was to reduce the amount of activity if we can't write
     anything out, so that bringing up a filesystem in "super ro" mode
     would be more lilkely to work for data recovery - but norecovery is
     the correct option for this.
  
   - btree_trans->locked; we now track whether a btree_trans has any btree
     nodes locked, and this is used for improved assertions related to
     trans_unlock() and trans_relock(). We'll also be using it for
     improving how we work with lockdep in the future: we don't want
     lockdep to be tracking individual btree node locks because we take
     too many for lockdep to track, and it's not necessary since we have a
     cycle detector.
  
   - Trigger improvements that are prep work for online fsck
  
   - BTREE_TRIGGER_check_repair; this regularizes how we do some repair
     work for extents that goes with running triggers in fsck, and fixes
     some subtle issues with transaction restarts there.
  
   - bch2_snapshot_equiv() has now been ripped out of fsck.c; snapshot
     equivalence classes are for when snapshot deletion leaves behind
     redundant snapshot nodes, but snapshot deletion now cleans this up
     right away, so the abstraction doesn't need to leak.
  
   - Improvements to how we resume writing to the journal in recovery. The
     code for picking the new place to write when reading the journal is
     greatly simplified and we also store the position in the superblock
     for when we don't read the journal; this means that we preserve more
     of the journal for list_journal debugging.
  
   - Improvements to sysfs btree_cache and btree_node_cache, for debugging
     memory reclaim.
  
   - We now detect when we've blocked for 10 seconds on the allocator in
     the write path and dump some useful info.
  
   - Safety fixes for devices references: this is a big series that
     changes almost all device lookups to properly check if the device
     exists and take a reference to it.
  
     Previously we assumed that if a bkey exists that references a device
     then the device must exist, and this was enforced in .invalid
     methods, but this was incorrect because it meant device removal
     relied on accounting being correct to not leave keys pointing to
     invalid devices, and that's not something we can assume.
  
     Getting the "pointer to invalid device" checks out of our .invalid()
     methods fixes some long standing device removal bugs; the only
     outstanding bug with device removal now is a race between the discard
     path and deleting alloc info, which should be easily fixed.
  
   - The allocator now prefers not to expand the new
     member_info.btree_allocated bitmap, meaning if repair ever requires
     scanning for btree nodes (because of a corrupt interior nodes) we
     won't have to scan the whole device(s).
  
   - New coding style document, which among other things talks about the
     correct usage of assertions
  
  * tag 'bcachefs-2024-05-19' of https://evilpiepirate.org/git/bcachefs: (155 commits)
    bcachefs: add no_invalid_checks flag
    bcachefs: add counters for failed shrinker reclaim
    bcachefs: Fix sb_field_downgrade validation
    bcachefs: Plumb bch_validate_flags to sb_field_ops.validate()
    bcachefs: s/bkey_invalid_flags/bch_validate_flags
    bcachefs: fsync() should not return -EROFS
    bcachefs: Invalid devices are now checked for by fsck, not .invalid methods
    bcachefs: kill bch2_dev_bkey_exists() in bch2_check_fix_ptrs()
    bcachefs: kill bch2_dev_bkey_exists() in bch2_read_endio()
    bcachefs: bch2_dev_get_ioref() checks for device not present
    bcachefs: bch2_dev_get_ioref2(); io_read.c
    bcachefs: bch2_dev_get_ioref2(); debug.c
    bcachefs: bch2_dev_get_ioref2(); journal_io.c
    bcachefs: bch2_dev_get_ioref2(); io_write.c
    bcachefs: bch2_dev_get_ioref2(); btree_io.c
    bcachefs: bch2_dev_get_ioref2(); backpointers.c
    bcachefs: bch2_dev_get_ioref2(); alloc_background.c
    bcachefs: for_each_bset() declares loop iter
    bcachefs: Move BCACHEFS_STATFS_MAGIC value to UAPI magic.h
    bcachefs: Improve sysfs internal/btree_cache
    ...
  ```
  </details>

- **2024-05-24**: Merge tag 'bcachefs-2024-05-24' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/c40b1994b9ffb45e19e6d83b7655d7b9db0174c3))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Nothing exciting, just syzbot fixes (except for the one
    FMODE_CAN_ODIRECT patch).
  
    Looks like syzbot reports have slowed down; this is all catch up from
    two weeks of conferences.
  
    Next hardening project is using Thomas's error injection tooling to
    torture test repair"
  
  * tag 'bcachefs-2024-05-24' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: Fix race path in bch2_inode_insert()
    bcachefs: Ensure we're RW before journalling
    bcachefs: Fix shutdown ordering
    bcachefs: Fix unsafety in bch2_dirent_name_bytes()
    bcachefs: Fix stack oob in __bch2_encrypt_bio()
    bcachefs: Fix btree_trans leak in bch2_readahead()
    bcachefs: Fix bogus verify_replicas_entry() assert
    bcachefs: Check for subvolues with bogus snapshot/inode fields
    bcachefs: bch2_checksum() returns 0 for unknown checksum type
    bcachefs: Fix bch2_alloc_ciphers()
    bcachefs: Add missing guard in bch2_snapshot_has_children()
    bcachefs: Fix missing parens in drop_locks_do()
    bcachefs: Improve bch2_assert_pos_locked()
    bcachefs: Fix shift overflows in replicas.c
    bcachefs: Fix shift overflow in btree_lost_data()
    bcachefs: Fix ref in trans_mark_dev_sbs() error path
    bcachefs: set FMODE_CAN_ODIRECT instead of a dummy direct_IO method
    bcachefs: Fix rcu splat in check_fix_ptrs()
  ```
  </details>

## RC2

- **2024-05-31**: Merge tag 'bcachefs-2024-05-30' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/ff9bce3d06fbdd12bcc74657516757b66aca9e43))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Assorted odds and ends...
  
     - two downgrade fixes
  
     - a couple snapshot deletion and repair fixes, thanks to noradtux for
       finding these and providing the image to debug them
  
     - a couple assert fixes
  
     - convert to folio helper, from Matthew
  
     - some improved error messages
  
     - bit of code reorganization (just moving things around); doing this
       while things are quiet so I'm not rebasing fixes past reorgs
  
     - don't return -EROFS on inconsistency error in recovery, this
       confuses util-linux and has it retry the mount
  
     - fix failure to return error on misaligned dio write; reported as an
       issue with coreutils shred"
  
  * tag 'bcachefs-2024-05-30' of https://evilpiepirate.org/git/bcachefs: (21 commits)
    bcachefs: Fix failure to return error on misaligned dio write
    bcachefs: Don't return -EROFS from mount on inconsistency error
    bcachefs: Fix uninitialized var warning
    bcachefs: Split out sb-errors_format.h
    bcachefs: Split out journal_seq_blacklist_format.h
    bcachefs: Split out replicas_format.h
    bcachefs: Split out disk_groups_format.h
    bcachefs: split out sb-downgrade_format.h
    bcachefs: split out sb-members_format.h
    bcachefs: Better fsck error message for key version
    bcachefs: btree_gc can now handle unknown btrees
    bcachefs: add missing MODULE_DESCRIPTION()
    bcachefs: Fix setting of downgrade recovery passes/errors
    bcachefs: Run check_key_has_snapshot in snapshot_delete_keys()
    bcachefs: Refactor delete_dead_snapshots()
    bcachefs: Fix locking assert
    bcachefs: Fix lookup_first_inode() when inode_generations are present
    bcachefs: Plumb bkey into __btree_err()
    bcachefs: Use copy_folio_from_iter_atomic()
    bcachefs: Fix sb-downgrade validation
    ...
  ```
  </details>

## RC3

- **2024-06-05**: Merge tag 'bcachefs-2024-06-05' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/e20b269d738b388e24f81fdf537cb4db7c693131))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Just a few small fixes"
  
  * tag 'bcachefs-2024-06-05' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: Fix trans->locked assert
    bcachefs: Rereplicate now moves data off of durability=0 devices
    bcachefs: Fix GFP_KERNEL allocation in break_cycle()
  ```
  </details>

## RC4

- **2024-06-12**: Merge tag 'bcachefs-2024-06-12' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/0b4989ebe8a608c68d5ec54d61078aba47baed22))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
  
   - fix kworker explosion, due to calling submit_bio() (which can block)
     from a multithreaded workqueue
  
   - fix error handling in btree node scan
  
   - forward compat fix: kill an old debug assert
  
   - key cache shrinker fixes
  
     This is a partial fix for stalls doing multithreaded creates - there
     were various O(n^2) issues the key cache shrinker was hitting [1].
  
     There's more work coming here; I'm working on a patch to delete the
     key cache lock, which initial testing shows to be a pretty drastic
     performance improvement
  
   - assorted syzbot fixes
  
  Link: https://lore.kernel.org/linux-bcachefs/CAGudoHGenxzk0ZqPXXi1_QDbfqQhGHu+wUwzyS6WmfkUZ1HiXA@mail.gmail.com/ [1]
  
  * tag 'bcachefs-2024-06-12' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: Fix rcu_read_lock() leak in drop_extra_replicas
    bcachefs: Add missing bch_inode_info.ei_flags init
    bcachefs: Add missing synchronize_srcu_expedited() call when shutting down
    bcachefs: Check for invalid bucket from bucket_gen(), gc_bucket()
    bcachefs: Replace bucket_valid() asserts in bucket lookup with proper checks
    bcachefs: Fix snapshot_create_lock lock ordering
    bcachefs: Fix refcount leak in check_fix_ptrs()
    bcachefs: Leave a buffer in the btree key cache to avoid lock thrashing
    bcachefs: Fix reporting of freed objects from key cache shrinker
    bcachefs: set sb->s_shrinker->seeks = 0
    bcachefs: increase key cache shrinker batch size
    bcachefs: Enable automatic shrinking for rhashtables
    bcachefs: fix the display format for show-super
    bcachefs: fix stack frame size in fsck.c
    bcachefs: Delete incorrect BTREE_ID_NR assertion
    bcachefs: Fix incorrect error handling found_btree_node_is_readable()
    bcachefs: Split out btree_write_submit_wq
  ```
  </details>

## RC5

- **2024-06-22**: Merge tag 'bcachefs-2024-06-22' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/c3de9b572fc2063fb62e53df50cc55156d6bfb45))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Lots of (mostly boring) fixes for syzbot bugs and rare(r) CI bugs.
  
    The LRU_TIME_BITS fix was slightly more involved; we only have 48 bits
    for the LRU position (we would prefer 64), so wraparound is possible
    for the cached data LRUs on a filesystem that has done sufficient
    (petabytes) reads; this is now handled.
  
    One notable user reported bugfix, where we were forgetting to
    correctly set the bucket data type, which should have been
    BCH_DATA_need_gc_gens instead of BCH_DATA_free; this was causing us to
    go emergency read-only on a filesystem that had seen heavy enough use
    to see bucket gen wraparoud.
  
    We're now starting to fix simple (safe) errors without requiring user
    intervention - i.e. a small incremental step towards full self
    healing.
  
    This is currently limited to just certain allocation information
    counters, and the error is still logged in the superblock; see that
    patch for more information. ("bcachefs: Fix safe errors by default")"
  
  * tag 'bcachefs-2024-06-22' of https://evilpiepirate.org/git/bcachefs: (22 commits)
    bcachefs: Move the ei_flags setting to after initialization
    bcachefs: Fix a UAF after write_super()
    bcachefs: Use bch2_print_string_as_lines for long err
    bcachefs: Fix I_NEW warning in race path in bch2_inode_insert()
    bcachefs: Replace bare EEXIST with private error codes
    bcachefs: Fix missing alloc_data_type_set()
    closures: Change BUG_ON() to WARN_ON()
    bcachefs: fix alignment of VMA for memory mapped files on THP
    bcachefs: Fix safe errors by default
    bcachefs: Fix bch2_trans_put()
    bcachefs: set_worker_desc() for delete_dead_snapshots
    bcachefs: Fix bch2_sb_downgrade_update()
    bcachefs: Handle cached data LRU wraparound
    bcachefs: Guard against overflowing LRU_TIME_BITS
    bcachefs: delete_dead_snapshots() doesn't need to go RW
    bcachefs: Fix early init error path in journal code
    bcachefs: Check for invalid btree IDs
    bcachefs: Fix btree ID bitmasks
    bcachefs: Fix shift overflow in read_one_super()
    bcachefs: Fix a locking bug in the do_discard_fast() path
    ...
  ```
  </details>

## RC6

- **2024-06-28**: Merge tag 'bcachefs-2024-06-28' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/cd63a278acedc375603820abff11a5414af53769))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
   "Simple stuff:
  
     - NULL ptr/err ptr deref fixes
  
     - fix for getting wedged on shutdown after journal error
  
     - fix missing recalc_capacity() call, capacity now changes correctly
       after a device goes read only
  
       however: our capacity calculation still doesn't take into account
       when we have mixed ro/rw devices and the ro devices have data on
       them, that's going to be a more involved fix to separate accounting
       for "capacity used on ro devices" and "capacity used on rw devices"
  
     - boring syzbot stuff
  
    Slightly more involved:
  
     - discard, invalidate workers are now per device
  
       this has the effect of simplifying how we take device refs in these
       paths, and the device ref cleanup fixes a longstanding race between
       the device removal path and the discard path
  
     - fixes for how the debugfs code takes refs on btree_trans objects we
       have debugfs code that prints in use btree_trans objects.
  
       It uses closure_get() on trans->ref, which is mainly for the cycle
       detector, but the debugfs code was using it on a closure that may
       have hit 0, which is not allowed; for performance reasons we cannot
       avoid having not-in-use transactions on the global list.
  
       Introduce some new primitives to fix this and make the
       synchronization here a whole lot saner"
  
  * tag 'bcachefs-2024-06-28' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: Fix kmalloc bug in __snapshot_t_mut
    bcachefs: Discard, invalidate workers are now per device
    bcachefs: Fix shift-out-of-bounds in bch2_blacklist_entries_gc
    bcachefs: slab-use-after-free Read in bch2_sb_errors_from_cpu
    bcachefs: Add missing bch2_journal_do_writes() call
    bcachefs: Fix null ptr deref in journal_pins_to_text()
    bcachefs: Add missing recalc_capacity() call
    bcachefs: Fix btree_trans list ordering
    bcachefs: Fix race between trans_put() and btree_transactions_read()
    closures: closure_get_not_zero(), closure_return_sync()
    bcachefs: Make btree_deadlock_to_text() clearer
    bcachefs: fix seqmutex_relock()
    bcachefs: Fix freeing of error pointers
  ```
  </details>

## final

- **2024-07-10**: Merge tag 'bcachefs-2024-07-10' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/f6963ab4b01cd92b9bf2eed0060907e35cc1440f))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull bcachefs fixes from Kent Overstreet:
  
   - Switch some asserts to WARN()
  
   - Fix a few "transaction not locked" asserts in the data read retry
     paths and backpointers gc
  
   - Fix a race that would cause the journal to get stuck on a flush
     commit
  
   - Add missing fsck checks for the fragmentation LRU
  
   - The usual assorted ssorted syzbot fixes
  
  * tag 'bcachefs-2024-07-10' of https://evilpiepirate.org/git/bcachefs: (22 commits)
    bcachefs: Add missing bch2_trans_begin()
    bcachefs: Fix missing error check in journal_entry_btree_keys_validate()
    bcachefs: Warn on attempting a move with no replicas
    bcachefs: bch2_data_update_to_text()
    bcachefs: Log mount failure error code
    bcachefs: Fix undefined behaviour in eytzinger1_first()
    bcachefs: Mark bch_inode_info as SLAB_ACCOUNT
    bcachefs: Fix bch2_inode_insert() race path for tmpfiles
    closures: fix closure_sync + closure debugging
    bcachefs: Fix journal getting stuck on a flush commit
    bcachefs: io clock: run timer fns under clock lock
    bcachefs: Repair fragmentation_lru in alloc_write_key()
    bcachefs: add check for missing fragmentation in check_alloc_to_lru_ref()
    bcachefs: bch2_btree_write_buffer_maybe_flush()
    bcachefs: Add missing printbuf_tabstops_reset() calls
    bcachefs: Fix loop restart in bch2_btree_transactions_read()
    bcachefs: Fix bch2_read_retry_nodecode()
    bcachefs: Don't use the new_fs() bucket alloc path on an initialized fs
    bcachefs: Fix shift greater than integer size
    bcachefs: Change bch2_fs_journal_stop() BUG_ON() to warning
    ...
  ```
  </details>

- **2024-07-12**: Merge tag 'bcachefs-2024-07-12' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/5d4c85134b0f76f72f975029bfa149e566ac968f))
  <details>
  <summary><span class="summary-closed-label">Show pull request</span><span class="summary-open-label">Hide pull request</span></summary>

  ```text
  Pull more bcachefs fixes from Kent Overstreet:
  
   - revert the SLAB_ACCOUNT patch, something crazy is going on in memcg
     and someone forgot to test
  
   - minor fixes: missing rcu_read_lock(), scheduling while atomic (in an
     emergency shutdown path)
  
   - two lockdep fixes; these could have gone earlier, but were left to
     bake awhile
  
  * tag 'bcachefs-2024-07-12' of https://evilpiepirate.org/git/bcachefs:
    bcachefs: bch2_gc_btree() should not use btree_root_lock
    bcachefs: Set PF_MEMALLOC_NOFS when trans->locked
    bcachefs; Use trans_unlock_long() when waiting on allocator
    Revert "bcachefs: Mark bch_inode_info as SLAB_ACCOUNT"
    bcachefs: fix scheduling while atomic in break_cycle()
    bcachefs: Fix RCU splat
  ```
  </details>
