+++
title = "Linux 6.7: bcachefs merges"
date = 2024-01-03T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.7.

## RC1

- 2023-10-30: Merge tag 'bcachefs-2023-10-30' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/9e87705289667a6c5185c619ea32f3d39314eb1b))

```text
Merge tag 'bcachefs-2023-10-30' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2023-10-30' of https://evilpiepirate.org/git/bcachefs

Pull initial bcachefs updates from Kent Overstreet:
 "Here's the bcachefs filesystem pull request.

  One new patch since last week: the exportfs constants ended up
  conflicting with other filesystems that are also getting added to the
  global enum, so switched to new constants picked by Amir.

  The only new non fs/bcachefs/ patch is the objtool patch that adds
  bcachefs functions to the list of noreturns. The patch that exports
  osq_lock() has been dropped for now, per Ingo"

* tag 'bcachefs-2023-10-30' of https://evilpiepirate.org/git/bcachefs: (2781 commits)
  exportfs: Change bcachefs fid_type enum to avoid conflicts
  bcachefs: Refactor memcpy into direct assignment
  bcachefs: Fix drop_alloc_keys()
  bcachefs: snapshot_create_lock
  bcachefs: Fix snapshot skiplists during snapshot deletion
  bcachefs: bch2_sb_field_get() refactoring
  bcachefs: KEY_TYPE_error now counts towards i_sectors
  bcachefs: Fix handling of unknown bkey types
  bcachefs: Switch to unsafe_memcpy() in a few places
  bcachefs: Use struct_size()
  bcachefs: Correctly initialize new buckets on device resize
  bcachefs: Fix another smatch complaint
  bcachefs: Use strsep() in split_devs()
  bcachefs: Add iops fields to bch_member
  bcachefs: Rename bch_sb_field_members -> bch_sb_field_members_v1
  bcachefs: New superblock section members_v2
  bcachefs: Add new helper to retrieve bch_member from sb
  bcachefs: bucket_lock() is now a sleepable lock
  bcachefs: fix crc32c checksum merge byte order problem
  bcachefs: Fix bch2_inode_delete_keys()
  ...
```

## RC2

<details>
<summary>Show merges (1)</summary>

- 2023-11-17: Merge tag 'bcachefs-2023-11-17' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/791c8ab095f71327899023223940dd52257a4173))

```text
Merge tag 'bcachefs-2023-11-17' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2023-11-17' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Lots of small fixes for minor nits and compiler warnings.

  Bigger items:

   - The six locks lost wakeup is finally fixed: six_read_trylock() was
     checking for the waiting bit before decrementing the number of
     readers - validated the fix with a torture test.

   - Fix for a memory reclaim issue: when needing to reallocate a key
     cache key, we now do our usual GFP_NOWAIT; unlock(); GFP_KERNEL
     dance.

   - Multiple deleted inodes btree fixes

   - Fix an issue in fsck, where i_nlink would be recalculated
     incorrectly for hardlinked files if a snapshot had ever been taken.

   - Kill journal pre-reservations: This is a bigger patch than I would
     normally send at this point, but it deletes code and it fixes some
     of our tests that would sporadically die with the journal getting
     stuck, and it's a performance improvement, too"

* tag 'bcachefs-2023-11-17' of https://evilpiepirate.org/git/bcachefs: (22 commits)
  bcachefs: Fix missing locking for dentry->d_parent access
  bcachefs: six locks: Fix lost wakeup
  bcachefs: Fix no_data_io mode checksum check
  bcachefs: Fix bch2_check_nlinks() for snapshots
  bcachefs: Don't decrease BTREE_ITER_MAX when LOCKDEP=y
  bcachefs: Disable debug log statements
  bcachefs: Fix missing transaction commit
  bcachefs: Fix error path in bch2_mount()
  bcachefs: Fix potential sleeping during mount
  bcachefs: Fix iterator leak in may_delete_deleted_inode()
  bcachefs: Kill journal pre-reservations
  bcachefs: Check for nonce offset inconsistency in data_update path
  bcachefs: Make sure to drop/retake btree locks before reclaim
  bcachefs: btree_trans->write_locked
  bcachefs: Run btree key cache shrinker less aggressively
  bcachefs: Split out btree_key_cache_types.h
  bcachefs: Guard against insufficient devices to create stripes
  bcachefs: Fix null ptr deref in bch2_backpointer_get_node()
  bcachefs: Fix multiple -Warray-bounds warnings
  bcachefs: Use DECLARE_FLEX_ARRAY() helper and fix multiple -Warray-bounds warnings
  ...
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2023-12-02: Merge tag 'bcachefs-2023-11-29' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/e6861be452a53a5de3e1a048eabd811a05a44915))

```text
Merge tag 'bcachefs-2023-11-29' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2023-11-29' of https://evilpiepirate.org/git/bcachefs

Pull more bcachefs bugfixes from Kent Overstreet:

 - bcache & bcachefs were broken with CFI enabled; patch for closures to
   fix type punning

 - mark erasure coding as extra-experimental; there are incompatible
   disk space accounting changes coming for erasure coding, and I'm
   still seeing checksum errors in some tests

 - several fixes for durability-related issues (durability is a device
   specific setting where we can tell bcachefs that data on a given
   device should be counted as replicated x times)

 - a fix for a rare livelock when a btree node merge then updates a
   parent node that is almost full

 - fix a race in the device removal path, where dropping a pointer in a
   btree node to a device would be clobbered by an in flight btree write
   updating the btree node key on completion

 - fix one SRCU lock hold time warning in the btree gc code - ther's
   still a bunch more of these to fix

 - fix a rare race where we'd start copygc before initializing the "are
   we rw" percpu refcount; copygc would think we were already ro and die
   immediately

* tag 'bcachefs-2023-11-29' of https://evilpiepirate.org/git/bcachefs: (23 commits)
  bcachefs: Extra kthread_should_stop() calls for copygc
  bcachefs: Convert gc_alloc_start() to for_each_btree_key2()
  bcachefs: Fix race between btree writes and metadata drop
  bcachefs: move journal seq assertion
  bcachefs: -EROFS doesn't count as move_extent_start_fail
  bcachefs: trace_move_extent_start_fail() now includes errcode
  bcachefs: Fix split_race livelock
  bcachefs: Fix bucket data type for stripe buckets
  bcachefs: Add missing validation for jset_entry_data_usage
  bcachefs: Fix zstd compress workspace size
  bcachefs: bpos is misaligned on big endian
  bcachefs: Fix ec + durability calculation
  bcachefs: Data update path won't accidentaly grow replicas
  bcachefs: deallocate_extra_replicas()
  bcachefs: Proper refcounting for journal_keys
  bcachefs: preserve device path as device name
  bcachefs: Fix an endianness conversion
  bcachefs: Start gc, copygc, rebalance threads after initing writes ref
  bcachefs: Don't stop copygc thread on device resize
  bcachefs: Make sure bch2_move_ratelimit() also waits for move_ops
  ...
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2023-12-11: Merge tag 'bcachefs-2023-12-10' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/26aff849438cebcd05f1a647390c4aa700d5c0f1))

```text
Merge tag 'bcachefs-2023-12-10' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2023-12-10' of https://evilpiepirate.org/git/bcachefs

Pull more bcachefs bugfixes from Kent Overstreet:

 - Fix a rare emergency shutdown path bug: dropping journal pins after
   the filesystem has mostly been torn down is not what we want.

 - Fix some concurrency issues with the btree write buffer and journal
   replay by not using the btree write buffer until journal replay is
   finished

 - A fixup from the prior patch to kill journal pre-reservations: at the
   start of the btree update path, where previously we took a
   pre-reservation, we do at least want to check the journal watermark.

 - Fix a race between dropping device metadata and btree node writes,
   which would re-add a pointer to a device that had just been dropped

 - Fix one of the SCRU lock warnings, in
   bch2_compression_stats_to_text().

 - Partial fix for a rare transaction paths overflow, when indirect
   extents had been split by background tasks, by not running certain
   triggers when they're not needed.

 - Fix for creating a snapshot with implicit source in a subdirectory of
   the containing subvolume

 - Don't unfreeze when we're emergency read-only

 - Fix for rebalance spinning trying to compress unwritten extentns

 - Another deleted_inodes fix, for directories

 - Fix a rare deadlock (usually just an unecessary wait) when flushing
   the journal with an open journal entry.

* tag 'bcachefs-2023-12-10' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: Close journal entry if necessary when flushing all pins
  bcachefs: Fix uninitialized var in bch2_journal_replay()
  bcachefs: Fix deleted inode check for dirs
  bcachefs: rebalance shouldn't attempt to compress unwritten extents
  bcachefs: don't attempt rw on unfreeze when shutdown
  bcachefs: Fix creating snapshot with implict source
  bcachefs: Don't run indirect extent trigger unless inserting/deleting
  bcachefs: Convert compression_stats to for_each_btree_key2
  bcachefs: Fix bch2_extent_drop_ptrs() call
  bcachefs: Fix a journal deadlock in replay
  bcachefs; Don't use btree write buffer until journal replay is finished
  bcachefs: Don't drop journal pins in exit path
```


</details>

## RC7

<details>
<summary>Show merges (1)</summary>

- 2023-12-20: Merge tag 'bcachefs-2023-12-19' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/74d8fc2b868ae156dcbd33132029561a8341d659))

```text
Merge tag 'bcachefs-2023-12-19' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2023-12-19' of https://evilpiepirate.org/git/bcachefs

Pull more bcachefs fixes from Kent Overstreet:

 - Fix a deadlock in the data move path with nocow locks (vs. update in
   place writes); when trylock failed we were incorrectly waiting for in
   flight ios to flush.

 - Fix reporting of NFS file handle length

 - Fix early error path in bch2_fs_alloc() - list head wasn't being
   initialized early enough

 - Make sure correct (hardware accelerated) crc modules get loaded

 - Fix a rare overflow in the btree split path, when the packed bkey
   format grows and all the keys have no value (LRU btree).

 - Fix error handling in the sector allocator

   This was causing writes to spuriously fail in multidevice setups, and
   another bug meant that the errors weren't being logged, only reported
   via fsync.

* tag 'bcachefs-2023-12-19' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: Fix bch2_alloc_sectors_start_trans() error handling
  bcachefs; guard against overflow in btree node split
  bcachefs: btree_node_u64s_with_format() takes nr keys
  bcachefs: print explicit recovery pass message only once
  bcachefs: improve modprobe support by providing softdeps
  bcachefs: fix invalid memory access in bch2_fs_alloc() error path
  bcachefs: Fix determining required file handle length
  bcachefs: Fix nocow locks deadlock
```


</details>

## RC8

<details>
<summary>Show merges (1)</summary>

- 2023-12-28: Merge tag 'bcachefs-2023-12-27' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/eeec2599630ac1ac03db98f3ba976975c72a1427))

```text
Merge tag 'bcachefs-2023-12-27' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2023-12-27' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Just a few fixes: besides a few one liners, we have a fix for
  snapshots + compression where the extent update path didn't account
  for the fact that with snapshots, we might split an existing extent
  into three, not just two; and a small fixup for promotes which were
  broken by the recent changes in the data update path to correctly take
  into account device durability"

* tag 'bcachefs-2023-12-27' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: Fix promotes
  bcachefs: Fix leakage of internal error code
  bcachefs: Fix insufficient disk reservation with compression + snapshots
  bcachefs: fix BCH_FSCK_ERR enum
```


</details>

## final

<details>
<summary>Show merges (1)</summary>

- 2024-01-03: Merge tag 'bcachefs-2024-01-01' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/981d04137a4b5ea95133572bdb3d888c9b515850))

```text
Merge tag 'bcachefs-2024-01-01' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-01-01' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs from Kent Overstreet:
 "More bcachefs bugfixes for 6.7, and forwards compatibility work:

   - fix for a nasty extents + snapshot interaction, reported when
     reflink of a snapshotted file wouldn't complete but turned out to
     be a more general bug

   - fix for an invalid free in dio write path when iov vector was
     longer than our inline vector

   - fix for a buffer overflow in the nocow write path -
     BCH_REPLICAS_MAX doesn't actually limit the number of pointers in
     an extent when cached pointers are included

   - RO snapshots are actually RO now

   - And, a new superblock section to avoid future breakage when the
     disk space acounting rewrite rolls out: the new superblock section
     describes versions that need work to downgrade, where the work
     required is a list of recovery passes and errors to silently fix"

* tag 'bcachefs-2024-01-01' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: make RO snapshots actually RO
  bcachefs: bch_sb_field_downgrade
  bcachefs: bch_sb.recovery_passes_required
  bcachefs: Add persistent identifiers for recovery passes
  bcachefs: prt_bitflags_vector()
  bcachefs: move BCH_SB_ERRS() to sb-errors_types.h
  bcachefs: fix buffer overflow in nocow write path
  bcachefs: DARRAY_PREALLOCATED()
  bcachefs: Switch darray to kvmalloc()
  bcachefs: Factor out darray resize slowpath
  bcachefs: fix setting version_upgrade_complete
  bcachefs: fix invalid free in dio write path
  bcachefs: Fix extents iteration + snapshots interaction
```


</details>
