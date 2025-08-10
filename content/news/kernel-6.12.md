+++
title = "Linux 6.12: bcachefs merges"
date = 2024-11-14T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.12.

## RC1

- 2024-09-29: Merge tag 'bcachefs-2024-09-28' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/9f9a53472452b83d44d5e1d77b6dea6eaa043204))

```text
Merge tag 'bcachefs-2024-09-28' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-09-28' of git://evilpiepirate.org/bcachefs

Pull more bcachefs updates from Kent Overstreet:
 "Assorted minor syzbot fixes, and for bigger stuff:

  Fix two disk accounting rewrite bugs:

   - Disk accounting keys use the version field of bkey so that journal
     replay can tell which updates have been applied to the btree.

     This is set in the transaction commit path, after we've gotten our
     journal reservation (and our time ordering), but the
     BCH_TRANS_COMMIT_skip_accounting_apply flag that journal replay
     uses was incorrectly skipping this for new updates generated prior
     to journal replay.

     This fixes the underlying cause of an assertion pop in
     disk_accounting_read.

   - A couple of fixes for disk accounting + device removal.

     Checking if acocunting replicas entries were marked in the
     superblock was being done at the wrong point, when deltas in the
     journal could still zero them out, and then additionally we'd try
     to add a missing replicas entry to the superblock without checking
     if it referred to an invalid (removed) device.

  A whole slew of repair fixes:

   - fix infinite loop in propagate_key_to_snapshot_leaves(), this fixes
     an infinite loop when repairing a filesystem with many snapshots

   - fix incorrect transaction restart handling leading to occasional
     "fsck counted ..." warnings

   - fix warning in __bch2_fsck_err() for bkey fsck errors

   - check_inode() in fsck now correctly checks if the filesystem was
     clean

   - there shouldn't be pending logged ops if the fs was clean, we now
     check for this

   - remove_backpointer() doesn't remove a dirent that doesn't actually
     point to the inode

   - many more fsck errors are AUTOFIX"

* tag 'bcachefs-2024-09-28' of git://evilpiepirate.org/bcachefs: (35 commits)
  bcachefs: check_subvol_path() now prints subvol root inode
  bcachefs: remove_backpointer() now checks if dirent points to inode
  bcachefs: dirent_points_to_inode() now warns on mismatch
  bcachefs: Fix lost wake up
  bcachefs: Check for logged ops when clean
  bcachefs: BCH_FS_clean_recovery
  bcachefs: Convert disk accounting BUG_ON() to WARN_ON()
  bcachefs: Fix BCH_TRANS_COMMIT_skip_accounting_apply
  bcachefs: Check for accounting keys with bversion=0
  bcachefs: rename version -> bversion
  bcachefs: Don't delete unlinked inodes before logged op resume
  bcachefs: Fix BCH_SB_ERRS() so we can reorder
  bcachefs: Fix fsck warnings from bkey validation
  bcachefs: Move transaction commit path validation to as late as possible
  bcachefs: Fix disk accounting attempting to mark invalid replicas entry
  bcachefs: Fix unlocked access to c->disk_sb.sb in bch2_replicas_entry_validate()
  bcachefs: Fix accounting read + device removal
  bcachefs: bch_accounting_mode
  bcachefs: fix transaction restart handling in check_extents(), check_dirents()
  bcachefs: kill inode_walker_entry.seen_this_pos
  ...
```

- 2024-09-23: Merge tag 'bcachefs-2024-09-21' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/b3f391fddf3cfaadda59ec8da8fd17f4520bbf42))

```text
Merge tag 'bcachefs-2024-09-21' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-09-21' of git://evilpiepirate.org/bcachefs

Pull bcachefs updates from Kent Overstreet:

 - rcu_pending, btree key cache rework: this solves lock contenting in
   the key cache, eliminating the biggest source of the srcu lock hold
   time warnings, and drastically improving performance on some metadata
   heavy workloads - on multithreaded creates we're now 3-4x faster than
   xfs.

 - We're now using an rhashtable instead of the system inode hash table;
   this is another significant performance improvement on multithreaded
   metadata workloads, eliminating more lock contention.

 - for_each_btree_key_in_subvolume_upto(): new helper for iterating over
   keys within a specific subvolume, eliminating a lot of open coded
   "subvolume_get_snapshot()" and also fixing another source of srcu
   lock time warnings, by running each loop iteration in its own
   transaction (as the existing for_each_btree_key() does).

 - More work on btree_trans locking asserts; we now assert that we don't
   hold btree node locks when trans->locked is false, which is important
   because we don't use lockdep for tracking individual btree node
   locks.

 - Some cleanups and improvements in the bset.c btree node lookup code,
   from Alan.

 - Rework of btree node pinning, which we use in backpointers fsck. The
   old hacky implementation, where the shrinker just skipped over nodes
   in the pinned range, was causing OOMs; instead we now use another
   shrinker with a much higher seeks number for pinned nodes.

 - Rebalance now uses BCH_WRITE_ONLY_SPECIFIED_DEVS; this fixes an issue
   where rebalance would sometimes fall back to allocating from the full
   filesystem, which is not what we want when it's trying to move data
   to a specific target.

 - Use __GFP_ACCOUNT, GFP_RECLAIMABLE for btree node, key cache
   allocations.

 - Idmap mounts are now supported (Hongbo Li)

 - Rename whiteouts are now supported (Hongbo Li)

 - Erasure coding can now handle devices being marked as failed, or
   forcibly removed. We still need the evacuate path for erasure coding,
   but it's getting very close to ready for people to start using.

* tag 'bcachefs-2024-09-21' of git://evilpiepirate.org/bcachefs: (99 commits)
  bcachefs: return err ptr instead of null in read sb clean
  bcachefs: Remove duplicated include in backpointers.c
  bcachefs: Don't drop devices with stripe pointers
  bcachefs: bch2_ec_stripe_head_get() now checks for change in rw devices
  bcachefs: bch_fs.rw_devs_change_count
  bcachefs: bch2_dev_remove_stripes()
  bcachefs: bch2_trigger_ptr() calculates sectors even when no device
  bcachefs: improve error messages in bch2_ec_read_extent()
  bcachefs: improve error message on too few devices for ec
  bcachefs: improve bch2_new_stripe_to_text()
  bcachefs: ec_stripe_head.nr_created
  bcachefs: bch_stripe.disk_label
  bcachefs: stripe_to_mem()
  bcachefs: EIO errcode cleanup
  bcachefs: Rework btree node pinning
  bcachefs: split up btree cache counters for live, freeable
  bcachefs: btree cache counters should be size_t
  bcachefs: Don't count "skipped access bit" as touched in btree cache scan
  bcachefs: Failed devices no longer require mounting in degraded mode
  bcachefs: bch2_dev_rcu_noerror()
  ...
```

## RC2

<details>
<summary>Show merges (1)</summary>

- 2024-10-05: Merge tag 'bcachefs-2024-10-05' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/8f602276d3902642fdc3429b548d73c745446601))

```text
Merge tag 'bcachefs-2024-10-05' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-10-05' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "A lot of little fixes, bigger ones include:

   - bcachefs's __wait_on_freeing_inode() was broken in rc1 due to vfs
     changes, now fixed along with another lost wakeup

   - fragmentation LRU fixes; fsck now repairs successfully (this is the
     data structure copygc uses); along with some nice simplification.

   - Rework logged op error handling, so that if logged op replay errors
     (due to another filesystem error) we delete the logged op instead
     of going into an infinite loop)

   - Various small filesystem connectivitity repair fixes"

* tag 'bcachefs-2024-10-05' of git://evilpiepirate.org/bcachefs:
  bcachefs: Rework logged op error handling
  bcachefs: Add warn param to subvol_get_snapshot, peek_inode
  bcachefs: Kill snapshot arg to fsck_write_inode()
  bcachefs: Check for unlinked, non-empty dirs in check_inode()
  bcachefs: Check for unlinked inodes with dirents
  bcachefs: Check for directories with no backpointers
  bcachefs: Kill alloc_v4.fragmentation_lru
  bcachefs: minor lru fsck fixes
  bcachefs: Mark more errors AUTOFIX
  bcachefs: Make sure we print error that causes fsck to bail out
  bcachefs: bkey errors are only AUTOFIX during read
  bcachefs: Create lost+found in correct snapshot
  bcachefs: Fix reattach_inode()
  bcachefs: Add missing wakeup to bch2_inode_hash_remove()
  bcachefs: Fix trans_commit disk accounting revert
  bcachefs: Fix bch2_inode_is_open() check
  bcachefs: Fix return type of dirent_points_to_inode_nowarn()
  bcachefs: Fix bad shift in bch2_read_flag_list()
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2024-10-15: Merge tag 'bcachefs-2024-10-14' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/bdc72765122356796aa72f6e99142cdf24254ce5))

```text
Merge tag 'bcachefs-2024-10-14' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-10-14' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - New metadata version inode_has_child_snapshots

   This fixes bugs with handling of unlinked inodes + snapshots, in
   particular when an inode is reattached after taking a snapshot;
   deleted inodes now get correctly cleaned up across snapshots.

 - Disk accounting rewrite fixes
     - validation fixes for when a device has been removed
     - fix journal replay failing with "journal_reclaim_would_deadlock"

 - Some more small fixes for erasure coding + device removal

 - Assorted small syzbot fixes

* tag 'bcachefs-2024-10-14' of git://evilpiepirate.org/bcachefs: (27 commits)
  bcachefs: Fix sysfs warning in fstests generic/730,731
  bcachefs: Handle race between stripe reuse, invalidate_stripe_to_dev
  bcachefs: Fix kasan splat in new_stripe_alloc_buckets()
  bcachefs: Add missing validation for bch_stripe.csum_granularity_bits
  bcachefs: Fix missing bounds checks in bch2_alloc_read()
  bcachefs: fix uaf in bch2_dio_write_done()
  bcachefs: Improve check_snapshot_exists()
  bcachefs: Fix bkey_nocow_lock()
  bcachefs: Fix accounting replay flags
  bcachefs: Fix invalid shift in member_to_text()
  bcachefs: Fix bch2_have_enough_devs() for BCH_SB_MEMBER_INVALID
  bcachefs: __wait_for_freeing_inode: Switch to wait_bit_queue_entry
  bcachefs: Check if stuck in journal_res_get()
  closures: Add closure_wait_event_timeout()
  bcachefs: Fix state lock involved deadlock
  bcachefs: Fix NULL pointer dereference in bch2_opt_to_text
  bcachefs: Release transaction before wake up
  bcachefs: add check for btree id against max in try read node
  bcachefs: Disk accounting device validation fixes
  bcachefs: bch2_inode_or_descendents_is_open()
  ...
```


</details>

## RC5

<details>
<summary>Show merges (1)</summary>

- 2024-10-24: Merge tag 'bcachefs-2024-10-22' of https://github.com/koverstreet/bcachefs ([commit](https://git.kernel.org/torvalds/c/c1e822754cc7f28b98c6897d62e8b47b4001e422))

```text
Merge tag 'bcachefs-2024-10-22' of https://github.com/koverstreet/bcachefs

Merge tag 'bcachefs-2024-10-22' of https://github.com/koverstreet/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Lots of hotfixes:

   - transaction restart injection has been shaking out a few things

   - fix a data corruption in the buffered write path on -ENOSPC, found
     by xfstests generic/299

   - Some small show_options fixes

   - Repair mismatches in inode hash type, seed: different snapshot
     versions of an inode must have the same hash/type seed, used for
     directory entries and xattrs. We were checking the hash seed, but
     not the type, and a user contributed a filesystem where the hash
     type on one inode had somehow been flipped; these fixes allow his
     filesystem to repair.

     Additionally, the hash type flip made some directory entries
     invisible, which were then recreated by userspace; so the hash
     check code now checks for duplicate non dangling dirents, and
     renames one of them if necessary.

   - Don't use wait_event_interruptible() in recovery: this fixes some
     filesystems failing to mount with -ERESTARTSYS

   - Workaround for kvmalloc not supporting > INT_MAX allocations,
     causing an -ENOMEM when allocating the sorted array of journal
     keys: this allows a 75 TB filesystem to mount

   - Make sure bch_inode_unpacked.bi_snapshot is set in the old inode
     compat path: this alllows Marcin's filesystem (in use since before
     6.7) to repair and mount"

* tag 'bcachefs-2024-10-22' of https://github.com/koverstreet/bcachefs: (26 commits)
  bcachefs: Set bch_inode_unpacked.bi_snapshot in old inode path
  bcachefs: Mark more errors as AUTOFIX
  bcachefs: Workaround for kvmalloc() not supporting > INT_MAX allocations
  bcachefs: Don't use wait_event_interruptible() in recovery
  bcachefs: Fix __bch2_fsck_err() warning
  bcachefs: fsck: Improve hash_check_key()
  bcachefs: bch2_hash_set_or_get_in_snapshot()
  bcachefs: Repair mismatches in inode hash seed, type
  bcachefs: Add hash seed, type to inode_to_text()
  bcachefs: INODE_STR_HASH() for bch_inode_unpacked
  bcachefs: Run in-kernel offline fsck without ratelimit errors
  bcachefs: skip mount option handle for empty string.
  bcachefs: fix incorrect show_options results
  bcachefs: Fix data corruption on -ENOSPC in buffered write path
  bcachefs: bch2_folio_reservation_get_partial() is now better behaved
  bcachefs: fix disk reservation accounting in bch2_folio_reservation_get()
  bcachefS: ec: fix data type on stripe deletion
  bcachefs: Don't use commit_do() unnecessarily
  bcachefs: handle restarts in bch2_bucket_io_time_reset()
  bcachefs: fix restart handling in __bch2_resume_logged_op_finsert()
  ...
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2024-11-01: Merge tag 'bcachefs-2024-10-31' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/7b83601da470cfdb0a66eb9335fb6ec34d3dd876))

```text
Merge tag 'bcachefs-2024-10-31' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-10-31' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Various syzbot fixes, and the more notable ones:

   - Fix for pointers in an extent overflowing the max (16) on a
     filesystem with many devices: we were creating too many cached
     copies when moving data around. Now, we only create at most one
     cached copy if there's a promote target set.

     Caching will be a bit broken for reflinked data until 6.13: I have
     larger series queued up which significantly improves the plumbing
     for data options down into the extent (bch_extent_rebalance) to fix
     this.

   - Fix for deadlock on -ENOSPC on tiny filesystems

     Allocation from the partial open_bucket list wasn't correctly
     accounting partial open_buckets as free: this fixes the main cause
     of tests timing out in the automated tests"

* tag 'bcachefs-2024-10-31' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix NULL ptr dereference in btree_node_iter_and_journal_peek
  bcachefs: fix possible null-ptr-deref in __bch2_ec_stripe_head_get()
  bcachefs: Fix deadlock on -ENOSPC w.r.t. partial open buckets
  bcachefs: Don't filter partial list buckets in open_buckets_to_text()
  bcachefs: Don't keep tons of cached pointers around
  bcachefs: init freespace inited bits to 0 in bch2_fs_initialize
  bcachefs: Fix unhandled transaction restart in fallocate
  bcachefs: Fix UAF in bch2_reconstruct_alloc()
  bcachefs: fix null-ptr-deref in have_stripes()
  bcachefs: fix shift oob in alloc_lru_idx_fragmentation
  bcachefs: Fix invalid shift in validate_sb_layout()
```


</details>

## RC7

<details>
<summary>Show merges (1)</summary>

- 2024-11-08: Merge tag 'bcachefs-2024-11-07' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/b5f1b488000068107869ab2553ab16b568f487b1))

```text
Merge tag 'bcachefs-2024-11-07' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-11-07' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Some trivial syzbot fixes, two more serious btree fixes found by
  looping single_devices.ktest small_nodes:

   - Topology error on split after merge, where we accidentaly picked
     the node being deleted for the pivot, resulting in an assertion pop

   - New nodes being preallocated were left on the freedlist, unlocked,
     resulting in them sometimes being accidentally freed: this dated
     from pre-cycle detector, when we could leave them locked. This
     should have resulted in more explosions and fireworks, but turned
     out to be surprisingly hard to hit because the preallocated nodes
     were being used right away.

     The fix for this is bigger than we'd like - reworking btree list
     handling was a bit invasive - but we've now got more assertions and
     it's well tested.

   - Also another mishandled transaction restart fix (in
     btree_node_prefetch) - we're almost done with those"

* tag 'bcachefs-2024-11-07' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix UAF in __promote_alloc() error path
  bcachefs: Change OPT_STR max to be 1 less than the size of choices array
  bcachefs: btree_cache.freeable list fixes
  bcachefs: check the invalid parameter for perf test
  bcachefs: add check NULL return of bio_kmalloc in journal_read_bucket
  bcachefs: Ensure BCH_FS_may_go_rw is set before exiting recovery
  bcachefs: Fix topology errors on split after merge
  bcachefs: Ancient versions with bad bkey_formats are no longer supported
  bcachefs: Fix error handling in bch2_btree_node_prefetch()
  bcachefs: Fix null ptr deref in bucket_gen_get()
```


</details>

## final

<details>
<summary>Show merges (1)</summary>

- 2024-11-14: Merge tag 'bcachefs-2024-11-13' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/4abcd80f23357808b0444d261ed08e5a77dbaa9a))

```text
Merge tag 'bcachefs-2024-11-13' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-11-13' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "This fixes one minor regression from the btree cache fixes (in the
  scan_for_btree_nodes repair path) - and the shutdown path fix is the
  big one here, in terms of bugs closed:

   - Assorted tiny syzbot fixes

   - Shutdown path fix: "bch2_btree_write_buffer_flush_going_ro()"

     The shutdown path wasn't flushing the btree write buffer, leading
     to shutting down while we still had operations in flight. This
     fixes a whole slew of syzbot bugs, and undoubtedly other strange
     heisenbugs.

* tag 'bcachefs-2024-11-13' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix assertion pop in bch2_ptr_swab()
  bcachefs: Fix journal_entry_dev_usage_to_text() overrun
  bcachefs: Allow for unknown key types in backpointers fsck
  bcachefs: Fix assertion pop in topology repair
  bcachefs: Fix hidden btree errors when reading roots
  bcachefs: Fix validate_bset() repair path
  bcachefs: Fix missing validation for bch_backpointer.level
  bcachefs: Fix bch_member.btree_bitmap_shift validation
  bcachefs: bch2_btree_write_buffer_flush_going_ro()
```


</details>
