+++
title = "Linux 6.9: bcachefs merges"
date = 2024-04-29T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.9.

## RC1

- 2024-03-19: Merge tag 'bcachefs-2024-03-19' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/a4145ce1e7bc247fd6f2846e8699473448717b37))

```text
Merge tag 'bcachefs-2024-03-19' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-03-19' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Assorted bugfixes.

  Most are fixes for simple assertion pops; the most significant fix is
  for a deadlock in recovery when we have to rewrite large numbers of
  btree nodes to fix errors. This was incorrectly running out of the
  same workqueue as the core interior btree update path - we now give it
  its own single threaded workqueue.

  This was visible to users as "bch2_btree_update_start(): error:
  BCH_ERR_journal_reclaim_would_deadlock" - and then recovery hanging"

* tag 'bcachefs-2024-03-19' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: Fix lost wakeup on journal shutdown
  bcachefs; Fix deadlock in bch2_btree_update_start()
  bcachefs: ratelimit errors from async_btree_node_rewrite
  bcachefs: Run check_topology() first
  bcachefs: Improve bch2_fatal_error()
  bcachefs: Fix lost transaction restart error
  bcachefs: Don't corrupt journal keys gap buffer when dropping alloc info
  bcachefs: fix for building in userspace
  bcachefs: bch2_snapshot_is_ancestor() now safe to call in early recovery
  bcachefs: Fix nested transaction restart handling in bch2_bucket_gens_init()
  bcachefs: Improve sysfs internal/btree_updates
  bcachefs: Split out btree_node_rewrite_worker
  bcachefs: Fix locking in bch2_alloc_write_key()
  bcachefs: Avoid extent entry type assertions in .invalid()
  bcachefs: Fix spurious -BCH_ERR_transaction_restart_nested
  bcachefs: Fix check_key_has_snapshot() call
  bcachefs: Change "accounting overran journal reservation" to a warning
```

- 2024-03-15: Merge tag 'bcachefs-2024-03-13' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/32a50540c3d26341698505998dfca5b0e8fb4fd4))

```text
Merge tag 'bcachefs-2024-03-13' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-03-13' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs updates from Kent Overstreet:

 - Subvolume children btree; this is needed for providing a userspace
   interface for walking subvolumes, which will come later

 - Lots of improvements to directory structure checking

 - Improved journal pipelining, significantly improving performance on
   high iodepth write workloads

 - Discard path improvements: the discard path is more efficient, and no
   longer flushes the journal unnecessarily

 - Buffered write path can now avoid taking the inode lock

 - new mm helper: memalloc_flags_{save|restore}

 - mempool now does kvmalloc mempools

* tag 'bcachefs-2024-03-13' of https://evilpiepirate.org/git/bcachefs: (128 commits)
  bcachefs: time_stats: shrink time_stat_buffer for better alignment
  bcachefs: time_stats: split stats-with-quantiles into a separate structure
  bcachefs: mean_and_variance: put struct mean_and_variance_weighted on a diet
  bcachefs: time_stats: add larger units
  bcachefs: pull out time_stats.[ch]
  bcachefs: reconstruct_alloc cleanup
  bcachefs: fix bch_folio_sector padding
  bcachefs: Fix btree key cache coherency during replay
  bcachefs: Always flush write buffer in delete_dead_inodes()
  bcachefs: Fix order of gc_done passes
  bcachefs: fix deletion of indirect extents in btree_gc
  bcachefs: Prefer struct_size over open coded arithmetic
  bcachefs: Kill unused flags argument to btree_split()
  bcachefs: Check for writing superblocks with nonsense member seq fields
  bcachefs: fix bch2_journal_buf_to_text()
  lib/generic-radix-tree.c: Make nodes more reasonably sized
  bcachefs: copy_(to|from)_user_errcode()
  bcachefs: Split out bkey_types.h
  bcachefs: fix lost journal buf wakeup due to improved pipelining
  bcachefs: intercept mountoption value for bool type
  ...
```

## RC3

<details>
<summary>Show merges (2)</summary>

- 2024-04-04: Merge tag 'bcachefs-2024-04-03' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/ec25bd8d981d910cdcc84914bf57e2cff9e7d63b))

```text
Merge tag 'bcachefs-2024-04-03' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-04-03' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs repair code from Kent Overstreet:
 "A couple more small fixes, and new repair code.

  We can now automatically recover from arbitrary corrupted interior
  btree nodes by scanning, and we can reconstruct metadata as needed to
  bring a filesystem back into a working, consistent, read-write state
  and preserve access to whatevver wasn't corrupted.

  Meaning - you can blow away all metadata except for extents and
  dirents leaf nodes, and repair will reconstruct everything else and
  give you your data, and under the correct paths. If inodes are missing
  i_size will be slightly off and permissions/ownership/timestamps will
  be gone, and we do still need the snapshots btree if snapshots were in
  use - in the future we'll be able to guess the snapshot tree structure
  in some situations.

  IOW - aside from shaking out remaining bugs (fuzz testing is still
  coming), repair code should be complete and if repair ever doesn't
  work that's the highest priority bug that I want to know about
  immediately.

  This patchset was kindly tested by a user from India who accidentally
  wiped one drive out of a three drive filesystem with no replication on
  the family computer - it took a couple weeks but we got everything
  important back"

* tag 'bcachefs-2024-04-03' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: reconstruct_inode()
  bcachefs: Subvolume reconstruction
  bcachefs: Check for extents that point to same space
  bcachefs: Reconstruct missing snapshot nodes
  bcachefs: Flag btrees with missing data
  bcachefs: Topology repair now uses nodes found by scanning to fill holes
  bcachefs: Repair pass for scanning for btree nodes
  bcachefs: Don't skip fake btree roots in fsck
  bcachefs: bch2_btree_root_alloc() -> bch2_btree_root_alloc_fake()
  bcachefs: Etyzinger cleanups
  bcachefs: bch2_shoot_down_journal_keys()
  bcachefs: Clear recovery_passes_required as they complete without errors
  bcachefs: ratelimit informational fsck errors
  bcachefs: Check for bad needs_discard before doing discard
  bcachefs: Improve bch2_btree_update_to_text()
  mean_and_variance: Drop always failing tests
  bcachefs: fix nocow lock deadlock
  bcachefs: BCH_WATERMARK_interior_updates
  bcachefs: Fix btree node reserve
```

- 2024-04-02: Merge tag 'bcachefs-2024-04-01' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/67199a47ddb9e265d1a83bb23bb06c752ffa1f4b))

```text
Merge tag 'bcachefs-2024-04-01' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-04-01' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Lots of fixes for situations with extreme filesystem damage.

  One fix ("Fix journal pins in btree write buffer") applicable to
  normal usage; also a dio performance fix.

  New repair/construction code is in the final stages, should be ready
  in about a week. Anyone that lost btree interior nodes (or a variety
  of other damage) as a result of the splitbrain bug will be able to
  repair then"

* tag 'bcachefs-2024-04-01' of https://evilpiepirate.org/git/bcachefs: (32 commits)
  bcachefs: On emergency shutdown, print out current journal sequence number
  bcachefs: Fix overlapping extent repair
  bcachefs: Fix remove_dirent()
  bcachefs: Logged op errors should be ignored
  bcachefs: Improve -o norecovery; opts.recovery_pass_limit
  bcachefs: bch2_run_explicit_recovery_pass_persistent()
  bcachefs: Ensure bch_sb_field_ext always exists
  bcachefs: Flush journal immediately after replay if we did early repair
  bcachefs: Resume logged ops after fsck
  bcachefs: Add error messages to logged ops fns
  bcachefs: Split out recovery_passes.c
  bcachefs: fix backpointer for missing alloc key msg
  bcachefs: Fix bch2_btree_increase_depth()
  bcachefs: Kill bch2_bkey_ptr_data_type()
  bcachefs: Fix use after free in check_root_trans()
  bcachefs: Fix repair path for missing indirect extents
  bcachefs: Fix use after free in bch2_check_fix_ptrs()
  bcachefs: Fix btree node keys accounting in topology repair path
  bcachefs: Check btree ptr min_key in .invalid
  bcachefs: add REQ_SYNC and REQ_IDLE in write dio
  ...
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2024-04-11: Merge tag 'bcachefs-2024-04-10' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/e1dc191dbf3f35cf07790b52110267bef55515a2))

```text
Merge tag 'bcachefs-2024-04-10' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-04-10' of https://evilpiepirate.org/git/bcachefs

Pull more bcachefs fixes from Kent Overstreet:
 "Notable user impacting bugs

   - On multi device filesystems, recovery was looping in
     btree_trans_too_many_iters(). This checks if a transaction has
     touched too many btree paths (because of iteration over many keys),
     and isuses a restart to drop unneeded paths.

     But it's now possible for some paths to exceed the previous limit
     without iteration in the interior btree update path, since the
     transaction commit will do alloc updates for every old and new
     btree node, and during journal replay we don't use the btree write
     buffer for locking reasons and thus those updates use btree paths
     when they wouldn't normally.

   - Fix a corner case in rebalance when moving extents on a
     durability=0 device. This wouldn't be hit when a device was
     formatted with durability=0 since in that case we'll only use it as
     a write through cache (only cached extents will live on it), but
     durability can now be changed on an existing device.

   - bch2_get_acl() could rarely forget to handle a transaction restart;
     this manifested as the occasional missing acl that came back after
     dropping caches.

   - Fix a major performance regression on high iops multithreaded write
     workloads (only since 6.9-rc1); a previous fix for a deadlock in
     the interior btree update path to check the journal watermark
     introduced a dependency on the state of btree write buffer flushing
     that we didn't want.

   - Assorted other repair paths and recovery fixes"

* tag 'bcachefs-2024-04-10' of https://evilpiepirate.org/git/bcachefs: (25 commits)
  bcachefs: Fix __bch2_btree_and_journal_iter_init_node_iter()
  bcachefs: Kill read lock dropping in bch2_btree_node_lock_write_nofail()
  bcachefs: Fix a race in btree_update_nodes_written()
  bcachefs: btree_node_scan: Respect member.data_allowed
  bcachefs: Don't scan for btree nodes when we can reconstruct
  bcachefs: Fix check_topology() when using node scan
  bcachefs: fix eytzinger0_find_gt()
  bcachefs: fix bch2_get_acl() transaction restart handling
  bcachefs: fix the count of nr_freed_pcpu after changing bc->freed_nonpcpu list
  bcachefs: Fix gap buffer bug in bch2_journal_key_insert_take()
  bcachefs: Rename struct field swap to prevent macro naming collision
  MAINTAINERS: Add entry for bcachefs documentation
  Documentation: filesystems: Add bcachefs toctree
  bcachefs: JOURNAL_SPACE_LOW
  bcachefs: Disable errors=panic for BCH_IOCTL_FSCK_OFFLINE
  bcachefs: Fix BCH_IOCTL_FSCK_OFFLINE for encrypted filesystems
  bcachefs: fix rand_delete unit test
  bcachefs: fix ! vs ~ typo in __clear_bit_le64()
  bcachefs: Fix rebalance from durability=0 device
  bcachefs: Print shutdown journal sequence number
  ...
```


</details>

## RC5

<details>
<summary>Show merges (1)</summary>

- 2024-04-15: Merge tag 'bcachefs-2024-04-15' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/cef27048e5c2f88677a647c336fae490e9c5492a))

```text
Merge tag 'bcachefs-2024-04-15' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-04-15' of https://evilpiepirate.org/git/bcachefs

Pull yet more bcachefs fixes from Kent Overstreet:
 "This gets recovery working again for the affected user I've been
  working with, and I'm still waiting to hear back on other bug reports
  but should fix it for everyone else who's been having issues with
  recovery.

   - Various recovery fixes:

       - fixes for the btree_insert_entry being resized on path
         allocation btree_path array recently became dynamically
         resizable, and btree_insert_entry along with it; this was being
         observed during journal replay, when write buffer btree updates
         don't use the write buffer and instead use the normal btree
         update path

       - multiple fixes for deadlock in recovery when we need to do lots
         of btree node merges; excessive merges were clocking up the
         whole pipeline

       - write buffer path now correctly does btree node merges when
         needed

       - fix failure to go RW when superblock indicates recovery passes
         needed (i.e. to complete an unfinished upgrade)

   - Various unsafety fixes - test case contributed by a user who had
     two drives out of a six drive array write out a whole bunch of
     garbage after power failure

   - New (tiny) on disk format feature: since it appears the btree node
     scan tool will be a more regular thing (crappy hardware, user
     error) - this adds a 64 bit per-device bitmap of regions that have
     ever had btree nodes.

   - A path->should_be_locked fix, from a larger patch series tightening
     up invariants and assertions around btree transaction and path
     locking state.

     This particular fix prevents us from keeping around btree_paths
     that are no longer needed"

* tag 'bcachefs-2024-04-15' of https://evilpiepirate.org/git/bcachefs: (24 commits)
  bcachefs: set_btree_iter_dontneed also clears should_be_locked
  bcachefs: fix error path of __bch2_read_super()
  bcachefs: Check for backpointer bucket_offset >= bucket size
  bcachefs: bch_member.btree_allocated_bitmap
  bcachefs: sysfs internal/trigger_journal_flush
  bcachefs: Fix bch2_btree_node_fill() for !path
  bcachefs: add safety checks in bch2_btree_node_fill()
  bcachefs: Interior known are required to have known key types
  bcachefs: add missing bounds check in __bch2_bkey_val_invalid()
  bcachefs: Fix btree node merging on write buffer btrees
  bcachefs: Disable merges from interior update path
  bcachefs: Run merges at BCH_WATERMARK_btree
  bcachefs: Fix missing write refs in fs fio paths
  bcachefs: Fix deadlock in journal replay
  bcachefs: Go rw if running any explicit recovery passes
  bcachefs: Standardize helpers for printing enum strs with bounds checks
  bcachefs: don't queue btree nodes for rewrites during scan
  bcachefs: fix race in bch2_btree_node_evict()
  bcachefs: fix unsafety in bch2_stripe_to_text()
  bcachefs: fix unsafety in bch2_extent_ptr_to_text()
  ...
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2024-04-22: Merge tag 'bcachefs-2024-04-22' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/a2c63a3f3d687ac4f63bf4ffa04d7458a2db350b))

```text
Merge tag 'bcachefs-2024-04-22' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-04-22' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Nothing too crazy in this one, and it looks like (fingers crossed) the
  recovery and repair issues are settling down - although there's going
  to be a long tail there, as we've still yet to really ramp up on error
  injection or syzbot.

   - fix a few more deadlocks in recovery

   - fix u32/u64 issues in mi_btree_bitmap

   - btree key cache shrinker now actually frees, with more
     instrumentation coming so we can verify that it's working
     correctly more easily in the future"

* tag 'bcachefs-2024-04-22' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: If we run merges at a lower watermark, they must be nonblocking
  bcachefs: Fix inode early destruction path
  bcachefs: Fix deadlock in journal write path
  bcachefs: Tweak btree key cache shrinker so it actually frees
  bcachefs: bkey_cached.btree_trans_barrier_seq needs to be a ulong
  bcachefs: Fix missing call to bch2_fs_allocator_background_exit()
  bcachefs: Check for journal entries overruning end of sb clean section
  bcachefs: Fix bio alloc in check_extent_checksum()
  bcachefs: fix leak in bch2_gc_write_reflink_key
  bcachefs: KEY_TYPE_error is allowed for reflink
  bcachefs: Fix bch2_dev_btree_bitmap_marked_sectors() shift
  bcachefs: make sure to release last journal pin in replay
  bcachefs: node scan: ignore multiple nodes with same seq if interior
  bcachefs: Fix format specifier in validate_bset_keys()
  bcachefs: Fix null ptr deref in twf from BCH_IOCTL_FSCK_OFFLINE
```


</details>

## RC7

<details>
<summary>Show merges (1)</summary>

- 2024-04-29: Merge tag 'bcachefs-2024-04-29' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/0a2e230514c5f1b09630bab94e457e930ced4cf0))

```text
Merge tag 'bcachefs-2024-04-29' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-04-29' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Tiny set of fixes this time"

* tag 'bcachefs-2024-04-29' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: fix integer conversion bug
  bcachefs: btree node scan now fills in sectors_written
  bcachefs: Remove accidental debug assert
```


</details>
