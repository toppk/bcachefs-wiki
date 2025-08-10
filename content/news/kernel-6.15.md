+++
title = "Linux 6.15: bcachefs merges"
date = 2025-05-22T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.15.

## RC1

- 2025-04-03: Merge tag 'bcachefs-2025-04-03' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/56770e24f678a84a21f21bcc1ae9cbc1364677bd))

```text
Merge tag 'bcachefs-2025-04-03' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-04-03' of git://evilpiepirate.org/bcachefs

Pull more bcachefs updates from Kent Overstreet:
 "More notable fixes:

   - Fix for striping behaviour on tiering filesystems where replicas
     exceeds durability on destination target

   - Fix a race in device removal where deleting alloc info races with
     the discard worker

   - Some small stack usage improvements: this is just enough for KMSAN
     builds to not blow the stack, more is queued up for 6.16"

* tag 'bcachefs-2025-04-03' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix "journal stuck" during recovery
  bcachefs: backpointer_get_key: check for null from peek_slot()
  bcachefs: Fix null ptr deref in invalidate_one_bucket()
  bcachefs: Fix check_snapshot_exists() restart handling
  bcachefs: use nonblocking variant of print_string_as_lines in error path
  bcachefs: Fix scheduling while atomic from logging changes
  bcachefs: Add error handling for zlib_deflateInit2()
  bcachefs: add missing selection of XARRAY_MULTI
  bcachefs: bch_dev_usage_full
  bcachefs: Kill btree_iter.trans
  bcachefs: do_trace_key_cache_fill()
  bcachefs: Split up bch_dev.io_ref
  bcachefs: fix ref leak in btree_node_read_all_replicas
  bcachefs: Fix null ptr deref in bch2_write_endio()
  bcachefs: Fix field spanning write warning
  bcachefs: Fix striping behaviour
```

- 2025-03-31: Merge tag 'bcachefs-2025-03-31' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/98fb679d19a17aec624d53b016953a3fcd272e8d))

```text
Merge tag 'bcachefs-2025-03-31' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-03-31' of git://evilpiepirate.org/bcachefs

Pull more bcachefs updates from Kent Overstreet:
 "All bugfixes and logging improvements"

* tag 'bcachefs-2025-03-31' of git://evilpiepirate.org/bcachefs: (35 commits)
  bcachefs: fix bch2_write_point_to_text() units
  bcachefs: Log original key being moved in data updates
  bcachefs: BCH_JSET_ENTRY_log_bkey
  bcachefs: Reorder error messages that include journal debug
  bcachefs: Don't use designated initializers for disk_accounting_pos
  bcachefs: Silence errors after emergency shutdown
  bcachefs: fix units in rebalance_status
  bcachefs: bch2_ioctl_subvolume_destroy() fixes
  bcachefs: Clear fs_path_parent on subvolume unlink
  bcachefs: Change btree_insert_node() assertion to error
  bcachefs: Better printing of inconsistency errors
  bcachefs: bch2_count_fsck_err()
  bcachefs: Better helpers for inconsistency errors
  bcachefs: Consistent indentation of multiline fsck errors
  bcachefs: Add an "ignore unknown" option to bch2_parse_mount_opts()
  bcachefs: bch2_time_stats_init_no_pcpu()
  bcachefs: Fix bch2_fs_get_tree() error path
  bcachefs: fix logging in journal_entry_err_msg()
  bcachefs: add missing newline in bch2_trans_updates_to_text()
  bcachefs: print_string_as_lines: fix extra newline
  ...
```

- 2025-03-27: Merge tag 'bcachefs-2025-03-24' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/4a4b30ea80d8cb5e8c4c62bb86201f4ea0d9b030))

```text
Merge tag 'bcachefs-2025-03-24' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-03-24' of git://evilpiepirate.org/bcachefs

Pull bcachefs updates from Kent Overstreet:
 "On disk format is now soft frozen: no more required/automatic are
  anticipated before taking off the experimental label.

  Major changes/features since 6.14:

   - Scrub

   - Blocksize greater than page size support

   - A number of "rebalance spinning and doing no work" issues have been
     fixed; we now check if the write allocation will succeed in
     bch2_data_update_init(), before kicking off the read.

     There's still more work to do in this area. Later we may want to
     add another bitset btree, like rebalance_work, to track "extents
     that rebalance was requested to move but couldn't", e.g. due to
     destination target having insufficient online devices.

   - We can now support scaling well into the petabyte range: latest
     bcachefs-tools will pick an appropriate bucket size at format time
     to ensure fsck can run in available memory (e.g. a server with
     256GB of ram and 100PB of storage would want 16MB buckets).

  On disk format changes:

   - 1.21: cached backpointers (scalability improvement)

     Cached replicas now get backpointers, which means we no longer rely
     on incrementing bucket generation numbers to invalidate cached
     data: this lets us get rid of the bucket generation number garbage
     collection, which had to periodically rescan all extents to
     recompute bucket oldest_gen.

     Bucket generation numbers are now only used as a consistency check,
     but they're quite useful for that.

   - 1.22: stripe backpointers

     Stripes now have backpointers: erasure coded stripes have their own
     checksums, separate from the checksums for the extents they contain
     (and stripe checksums also cover the parity blocks). This is
     required for implementing scrub for stripes.

   - 1.23: stripe lru (scalability improvement)

     Persistent lru for stripes, ordered by "number of empty blocks".
     This is used by the stripe creation path, which depending on free
     space may create a new stripe out of a partially empty existing
     stripe instead of starting a brand new stripe.

     This replaces an in-memory heap, and means we no longer have to
     read in the stripes btree at startup.

   - 1.24: casefolding

     Case insensitive directory support, courtesy of Valve.

     This is an incompatible feature, to enable mount with
       -o version_upgrade=incompatible

   - 1.25: extent_flags

     Another incompatible feature requiring explicit opt-in to enable.

     This adds a flags entry to extents, and a flag bit that marks
     extents as poisoned.

     A poisoned extent is an extent that was unreadable due to checksum
     errors. We can't move such extents without giving them a new
     checksum, and we may have to move them (for e.g. copygc or device
     evacuate). We also don't want to delete them: in the future we'll
     have an API that lets userspace ignore checksum errors and attempt
     to deal with simple bitrot itself. Marking them as poisoned lets us
     continue to return the correct error to userspace on normal read
     calls.

  Other changes/features:

   - BCH_IOCTL_QUERY_COUNTERS: this is used by the new 'bcachefs fs top'
     command, which shows a live view of all internal filesystem
     counters.

   - Improved journal pipelining: we can now have 16 journal writes in
     flight concurrently, up from 4. We're logging significantly more to
     the journal than we used to with all the recent disk accounting
     changes and additions, so some users should see a performance
     increase on some workloads.

   - BCH_MEMBER_STATE_failed: previously, we would do no IO at all to
     devices marked as failed. Now we will attempt to read from them,
     but only if we have no better options.

   - New option, write_error_timeout: devices will be kicked out of the
     filesystem if all writes have been failing for x number of seconds.

     We now also kick devices out when notified by blk_holder_ops that
     they've gone offline.

   - Device option handling improvements: the discard option should now
     be working as expected (additionally, in -tools, all device options
     that can be set at format time can now be set at device add time,
     i.e. data_allowed, state).

   - We now try harder to read data after a checksum error: we'll do
     additional retries if necessary to a device after after it gave us
     data with a checksum error.

   - More self healing work: the full inode <-> dirent consistency
     checks that are currently run by fsck are now also run every time
     we do a lookup, meaning we'll be able to correct errors at runtime.
     Runtime self healing will be flipped on after the new changes have
     seen more testing, currently they're just checking for consistency.

   - KMSAN fixes: our KMSAN builds should be nearly clean now, which
     will put a massive dent in the syzbot dashboard"

* tag 'bcachefs-2025-03-24' of git://evilpiepirate.org/bcachefs: (180 commits)
  bcachefs: Kill unnecessary bch2_dev_usage_read()
  bcachefs: btree node write errors now print btree node
  bcachefs: Fix race in print_chain()
  bcachefs: btree_trans_restart_foreign_task()
  bcachefs: bch2_disk_accounting_mod2()
  bcachefs: zero init journal bios
  bcachefs: Eliminate padding in move_bucket_key
  bcachefs: Fix a KMSAN splat in btree_update_nodes_written()
  bcachefs: kmsan asserts
  bcachefs: Fix kmsan warnings in bch2_extent_crc_pack()
  bcachefs: Disable asm memcpys when kmsan enabled
  bcachefs: Handle backpointers with unknown data types
  bcachefs: Count BCH_DATA_parity backpointers correctly
  bcachefs: Run bch2_check_dirent_target() at lookup time
  bcachefs: Refactor bch2_check_dirent_target()
  bcachefs: Move bch2_check_dirent_target() to namei.c
  bcachefs: fs-common.c -> namei.c
  bcachefs: EIO cleanup
  bcachefs: bch2_write_prep_encoded_data() now returns errcode
  bcachefs: Simplify bch2_write_op_error()
  ...
```

## RC2

<details>
<summary>Show merges (1)</summary>

- 2025-04-10: Merge tag 'bcachefs-2025-04-10' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/ef7785882672e73847fb80f6c39e76998d4db57b))

```text
Merge tag 'bcachefs-2025-04-10' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-04-10' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Mostly minor fixes.

  Eric Biggers' crypto API conversion is included because of long
  standing sporadic crashes - mostly, but not entirely syzbot - in the
  crypto API code when calling poly1305, which have been nigh impossible
  to reproduce and debug.

  His rework deletes the code where we've seen the crashes, so either
  it'll be a fix or we'll end up with backtraces we can debug. (Thanks
  Eric!)"

* tag 'bcachefs-2025-04-10' of git://evilpiepirate.org/bcachefs:
  bcachefs: Use sort_nonatomic() instead of sort()
  bcachefs: Remove unnecessary softdep on xxhash
  bcachefs: use library APIs for ChaCha20 and Poly1305
  bcachefs: Fix duplicate "ro,read_only" in opts at startup
  bcachefs: Fix UAF in bchfs_read()
  bcachefs: Use cpu_to_le16 for dirent lengths
  bcachefs: Fix type for parameter in journal_advance_devs_to_next_bucket
  bcachefs: Fix escape sequence in prt_printf
```


</details>

## RC3

<details>
<summary>Show merges (1)</summary>

- 2025-04-17: Merge tag 'bcachefs-2025-04-17' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/9e99c1accb1df0b07e409ce21f15fa4e8ddca28f))

```text
Merge tag 'bcachefs-2025-04-17' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-04-17' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Usual set of small fixes/logging improvements.

  One bigger user reported fix, for inode <-> dirent inconsistencies
  reported in fsck, after moving a subvolume that had been snapshotted"

* tag 'bcachefs-2025-04-17' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix snapshotting a subvolume, then renaming it
  bcachefs: Add missing READ_ONCE() for metadata replicas
  bcachefs: snapshot_node_missing is now autofix
  bcachefs: Log message when incompat version requested but not enabled
  bcachefs: Print version_incompat_allowed on startup
  bcachefs: Silence extent_poisoned error messages
  bcachefs: btree_root_unreadable_and_scan_found_nothing now AUTOFIX
  bcachefs: fix bch2_dev_usage_full_read_fast()
  bcachefs: Don't print data read retry success on non-errors
  bcachefs: Add missing error handling
  bcachefs: Prevent granting write refs when filesystem is read-only
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2025-04-25: Merge tag 'bcachefs-2025-04-24' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/eef0dc0bd432885b2bd4fc7f410ed039bf028e37))

```text
Merge tag 'bcachefs-2025-04-24' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-04-24' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - Case insensitive directories now work

 - Ciemap now correctly reports on unwritten pagecache data

 - bcachefs tools 1.25.1 was incorrectly picking unaligned bucket sizes;
   fix journal and write path bugs this uncovered

And assorted smaller fixes...

* tag 'bcachefs-2025-04-24' of git://evilpiepirate.org/bcachefs: (24 commits)
  bcachefs: Rework fiemap transaction restart handling
  bcachefs: add fiemap delalloc extent detection
  bcachefs: refactor fiemap processing into extent helper and struct
  bcachefs: track current fiemap offset in start variable
  bcachefs: drop duplicate fiemap sync flag
  bcachefs: Fix btree_iter_peek_prev() at end of inode
  bcachefs: Make btree_iter_peek_prev() assert more precise
  bcachefs: Unit test fixes
  bcachefs: Print mount opts earlier
  bcachefs: unlink: casefold d_invalidate
  bcachefs: Fix casefold lookups
  bcachefs: Casefold is now a regular opts.h option
  bcachefs: Implement fileattr_(get|set)
  bcachefs: Allocator now copes with unaligned buckets
  bcachefs: Start copygc, rebalance threads earlier
  bcachefs: Refactor bch2_run_recovery_passes()
  bcachefs: bch2_copygc_wakeup()
  bcachefs: Fix ref leak in write_super()
  bcachefs: Change __journal_entry_close() assert to ERO
  bcachefs: Ensure journal space is block size aligned
  ...
```


</details>

## RC5

<details>
<summary>Show merges (1)</summary>

- 2025-05-02: Merge tag 'bcachefs-2025-05-01' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/2bfcee565c3a36f2781152a767d34c9dc5432f95))

```text
Merge tag 'bcachefs-2025-05-01' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-05-01' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Lots of assorted small fixes...

   - Some repair path fixes, a fix for -ENOMEM when reconstructing lots
     of alloc info on large filesystems, upgrade for ancient 0.14
     filesystems, etc.

   - Various assert tweaks; assert -> ERO, ERO -> log the error in the
     superblock and continue

   - casefolding now uses d_ops like on other casefolding filesystems

   - fix device label create on device add, fix bucket array resize on
     filesystem resize

   - fix xattrs with FORTIFY_SOURCE builds with gcc-15/clang"

* tag 'bcachefs-2025-05-01' of git://evilpiepirate.org/bcachefs: (22 commits)
  bcachefs: Remove incorrect __counted_by annotation
  bcachefs: add missing sched_annotate_sleep()
  bcachefs: Fix __bch2_dev_group_set()
  bcachefs: Kill ERO for i_blocks check in truncate
  bcachefs: check for inode.bi_sectors underflow
  bcachefs: Kill ERO in __bch2_i_sectors_acct()
  bcachefs: readdir fixes
  bcachefs: improve missing journal write device error message
  bcachefs: Topology error after insert is now an ERO
  bcachefs: Use bch2_kvmalloc() for journal keys array
  bcachefs: More informative error message when shutting down due to error
  bcachefs: btree_root_unreadable_and_scan_found_nothing autofix for non data btrees
  bcachefs: btree_node_data_missing is now autofix
  bcachefs: Don't generate alloc updates to invalid buckets
  bcachefs: Improve bch2_dev_bucket_missing()
  bcachefs: fix bch2_dev_buckets_resize()
  bcachefs: Add upgrade table entry from 0.14
  bcachefs: Run BCH_RECOVERY_PASS_reconstruct_snapshots on missing subvol -> snapshot
  bcachefs: Add missing utf8_unload()
  bcachefs: Emit unicode version message on startup
  ...
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2025-05-08: Merge tag 'bcachefs-2025-05-08' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/9c69f88849045499e8ad114e5e13dbb3c85f4443))

```text
Merge tag 'bcachefs-2025-05-08' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-05-08' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - Some fixes to help with filesystem analysis: ensure superblock
   error count gets written if we go ERO, don't discard the journal
   aggressively (so it's available for list_journal -a)

 - Fix lost wakeup on arm causing us to get stuck when reading btree
   nodes

 - Fix fsck failing to exit on ctrl-c

 - An additional fix for filesystems with misaligned bucket sizes: we
   now ensure that allocations are properly aligned

 - Setting background target but not promote target will now leave that
   data cached on the foreground target, as it used to

 - Revert a change to when we allocate the VFS superblock, this was done
   for implementing blk_holder_ops but ended up not being needed, and
   allocating a superblock and not setting SB_BORN while we do recovery
   caused sync() calls and other things to hang

 - Assorted fixes for harmless error messages that caused concern to
   users

* tag 'bcachefs-2025-05-08' of git://evilpiepirate.org/bcachefs:
  bcachefs: Don't aggressively discard the journal
  bcachefs: Ensure superblock gets written when we go ERO
  bcachefs: Filter out harmless EROFS error messages
  bcachefs: journal_shutdown is EROFS, not EIO
  bcachefs: Call bch2_fs_start before getting vfs superblock
  bcachefs: fix hung task timeout in journal read
  bcachefs: Add missing barriers before wake_up_bit()
  bcachefs: Ensure proper write alignment
  bcachefs: Improve want_cached_ptr()
  bcachefs: thread_with_stdio: fix spinning instead of exiting
```


</details>

## RC7

<details>
<summary>Show merges (1)</summary>

- 2025-05-15: Merge tag 'bcachefs-2025-05-15' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/fee3e843b309444f48157e2188efa6818bae85cf))

```text
Merge tag 'bcachefs-2025-05-15' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-05-15' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "The main user reported ones are:

   - Fix a btree iterator locking inconsistency that's been causing us
     to go emergency read-only in evacuate: "Fix broken btree_path lock
     invariants in next_node()"

   - Minor btree node cache reclaim tweak that should help with OOMs:
     don't set btree nodes as accessed on fill

   - Fix a bch2_bkey_clear_rebalance() issue that was causing rebalance
     to do needless work"

* tag 'bcachefs-2025-05-15' of git://evilpiepirate.org/bcachefs:
  bcachefs: fix wrong arg to fsck_err()
  bcachefs: Fix missing commit in backpointer to missing target
  bcachefs: Fix accidental O(n^2) in fiemap
  bcachefs: Fix set_should_be_locked() call in peek_slot()
  bcachefs: Fix self deadlock
  bcachefs: Don't set btree nodes as accessed on fill
  bcachefs: Fix livelock in journal_entry_open()
  bcachefs: Fix broken btree_path lock invariants in next_node()
  bcachefs: Don't strip rebalance_opts from indirect extents
```


</details>

## final

<details>
<summary>Show merges (1)</summary>

- 2025-05-22: Merge tag 'bcachefs-2025-05-22' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/040c0f6a187162f082578b431b5919856c3df820))

```text
Merge tag 'bcachefs-2025-05-22' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-05-22' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Small stuff, main ones users will be interested in:

   - Couple more casefolding fixes; we can now detect and repair
     casefolded dirents in non-casefolded dir and vice versa

   - Fix for massive write inflation with mmapped io, which hit certain
     databases"

* tag 'bcachefs-2025-05-22' of git://evilpiepirate.org/bcachefs:
  bcachefs: Check for casefolded dirents in non casefolded dirs
  bcachefs: Fix bch2_dirent_create_snapshot() for casefolding
  bcachefs: Fix casefold opt via xattr interface
  bcachefs: mkwrite() now only dirties one page
  bcachefs: fix extent_has_stripe_ptr()
  bcachefs: Fix bch2_btree_path_traverse_cached() when paths realloced
```


</details>
