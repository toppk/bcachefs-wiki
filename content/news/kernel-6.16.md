+++
title = "Linux 6.16: bcachefs merges"
date = 2025-07-25T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.16.

## RC1

- 2025-06-04: Merge tag 'bcachefs-2025-06-04' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/ff0905bbf991f4337b5ebc19c0d43525ebb0d96b))

```text
Merge tag 'bcachefs-2025-06-04' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-06-04' of git://evilpiepirate.org/bcachefs

Pull more bcachefs updates from Kent Overstreet:
 "More bcachefs updates:

   - More stack usage improvements (~600 bytes)

   - Define CLASS()es for some commonly used types, and convert most
     rcu_read_lock() uses to the new lock guards

   - New introspection:
       - Superblock error counters are now available in sysfs:
         previously, they were only visible with 'show-super', which
         doesn't provide a live view
       - New tracepoint, error_throw(), which is called any time we
         return an error and start to unwind

   - Repair
       - check_fix_ptrs() can now repair btree node roots
       - We can now repair when we've somehow ended up with the journal
         using a superblock bucket

   - Revert some leftovers from the aborted directory i_size feature,
     and add repair code: some userspace programs (e.g. sshfs) were
     getting confused

  It seems in 6.15 there's a bug where i_nlink on the vfs inode has been
  getting incorrectly set to 0, with some unfortunate results;
  list_journal analysis showed bch2_inode_rm() being called (by
  bch2_evict_inode()) when it clearly should not have been.

   - bch2_inode_rm() now runs "should we be deleting this inode?" checks
     that were previously only run when deleting unlinked inodes in
     recovery

   - check_subvol() was treating a dangling subvol (pointing to a
     missing root inode) like a dangling dirent, and deleting it. This
     was the really unfortunate one: check_subvol() will now recreate
     the root inode if necessary

  This took longer to debug than it should have, and we lost several
  filesystems unnecessarily, because users have been ignoring the
  release notes and blindly running 'fsck -y'. Debugging required
  reconstructing what happened through analyzing the journal, when
  ideally someone would have noticed 'hey, fsck is asking me if I want
  to repair this: it usually doesn't, maybe I should run this in dry run
  mode and check what's going on?'

  As a reminder, fsck errors are being marked as autofix once we've
  verified, in real world usage, that they're working correctly; blindly
  running 'fsck -y' on an experimental filesystem is playing with fire

  Up to this incident we've had an excellent track record of not losing
  data, so let's try to learn from this one

  This is a community effort, I wouldn't be able to get this done
  without the help of all the people QAing and providing excellent bug
  reports and feedback based on real world usage. But please don't
  ignore advice and expect me to pick up the pieces

  If an error isn't marked as autofix, and it /is/ happening in the
  wild, that's also something I need to know about so we can check it
  out and add it to the autofix list if repair looks good. I haven't
  been getting those reports, and I should be; since we don't have any
  sort of telemetry yet I am absolutely dependent on user reports

  Now I'll be spending the weekend working on new repair code to see if
  I can get a filesystem back for a user who didn't have backups"

* tag 'bcachefs-2025-06-04' of git://evilpiepirate.org/bcachefs: (69 commits)
  bcachefs: add cond_resched() to handle_overwrites()
  bcachefs: Make journal read log message a bit quieter
  bcachefs: Fix subvol to missing root repair
  bcachefs: Run may_delete_deleted_inode() checks in bch2_inode_rm()
  bcachefs: delete dead code from may_delete_deleted_inode()
  bcachefs: Add flags to subvolume_to_text()
  bcachefs: Fix oops in btree_node_seq_matches()
  bcachefs: Fix dirent_casefold_mismatch repair
  bcachefs: Fix bch2_fsck_rename_dirent() for casefold
  bcachefs: Redo bch2_dirent_init_name()
  bcachefs: Fix -Wc23-extensions in bch2_check_dirents()
  bcachefs: Run check_dirents second time if required
  bcachefs: Run snapshot deletion out of system_long_wq
  bcachefs: Make check_key_has_snapshot safer
  bcachefs: BCH_RECOVERY_PASS_NO_RATELIMIT
  bcachefs: bch2_require_recovery_pass()
  bcachefs: bch_err_throw()
  bcachefs: Repair code for directory i_size
  bcachefs: Kill un-reverted directory i_size code
  bcachefs: Delete redundant fsck_err()
  ...
```

- 2025-05-26: Merge tag 'bcachefs-2025-05-24' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/522544fc71c27b4b432386c7919f71ecc79a3bfb))

```text
Merge tag 'bcachefs-2025-05-24' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-05-24' of git://evilpiepirate.org/bcachefs

Pull bcachefs updates from Kent Overstreet:

 - Poisoned extents can now be moved: this lets us handle bitrotted data
   without deleting it. For now, reading from poisoned extents only
   returns -EIO: in the future we'll have an API for specifying "read
   this data even if there were bitflips".

 - Incompatible features may now be enabled at runtime, via
   "opts/version_upgrade" in sysfs. Toggle it to incompatible, and then
   toggle it back - option changes via the sysfs interface are
   persistent.

 - Various changes to support deployable disk images:

     - RO mounts now use less memory

     - Images may be stripped of alloc info, particularly useful for
       slimming them down if they will primarily be mounted RO. Alloc
       info will be automatically regenerated on first RW mount, and
       this is quite fast

     - Filesystem images generated with 'bcachefs image' will be
       automatically resized the first time they're mounted on a larger
       device

   The images 'bcachefs image' generates with compression enabled have
   been comparable in size to those generated by squashfs and erofs -
   but you get a full RW capable filesystem

 - Major error message improvements for btree node reads, data reads,
   and elsewhere. We now build up a single error message that lists all
   the errors encountered, actions taken to repair, and success/failure
   of the IO. This extends to other error paths that may kick off other
   actions, e.g. scheduling recovery passes: actions we took because of
   an error are included in that error message, with
   grouping/indentation so we can see what caused what.

 - New option, 'rebalance_on_ac_only'. Does exactly what the name
   suggests, quite handy with background compression.

 - Repair/self healing:

     - We can now kick off recovery passes and run them in the
       background if we detect errors. Currently, this is just used by
       code that walks backpointers. We now also check for missing
       backpointers at runtime and run check_extents_to_backpointers if
       required. The messy 6.14 upgrade left missing backpointers for
       some users, and this will correct that automatically instead of
       requiring a manual fsck - some users noticed this as copygc
       spinning and not making progress.

       In the future, as more recovery passes come online, we'll be able
       to repair and recover from nearly anything - except for
       unreadable btree nodes, and that's why you're using replication,
       of course - without shutting down the filesystem.

     - There's a new recovery pass, for checking the rebalance_work
       btree, which tracks extents that rebalance will process later.

 - Hardening:

     - Close the last known hole in btree iterator/btree locking
       assertions: path->should_be_locked paths must stay locked until
       the end of the transaction. This shook out a few bugs, including
       a performance issue that was causing unnecessary path_upgrade
       transaction restarts.

 - Performance:

     - Faster snapshot deletion: this is an incompatible feature, as it
       requires new sentinal values, for safety. Snapshot deletion no
       longer has to do a full metadata scan, it now just scans the
       inodes btree: if an extent/dirent/xattr is present for a given
       snapshot ID, we already require that an inode be present with
       that same snapshot ID.

       If/when users hit scalability limits again (ridiculously huge
       filesystems with lots of inodes, and many sparse snapshots), let
       me know - the next step will be to add an index from snapshot ID
       -> inode number, which won't be too hard.

     - Faster device removal: the "scan for pointers to this device" no
       longer does a full metadata scan, instead it walks backpointers.
       Like fast snapshot deletion this is another incompat feature: it
       also requires a new sentinal value, because we don't want to
       reuse these device IDs until after a fsck.

     - We're now coalescing redundant accounting updates prior to
       transaction commit, taking some pressure off the journal. Shortly
       we'll also be doing multiple extent updates in a transaction in
       the main write path, which combined with the previous should
       drastically cut down on the amount of metadata updates we have to
       journal.

 - Stack usage improvements: All allocator state has been moved off the
   stack

 - Debug improvements:

     - enumerated refcounts: The debug code previously used for
       filesystem write refs is now a small library, and used for other
       heavily used refcounts. Different users of a refcount are
       enumerated, making it much easier to debug refcount issues.

     - Async object debugging: There's a new kconfig option that makes
       various async objects (different types of bios, data updates,
       write ops, etc.) visible in debugfs, and it should be fast enough
       to leave on in production.

     - Various sets of assertions no longer require
       CONFIG_BCACHEFS_DEBUG, instead they're controlled by module
       parameters and static keys, meaning users won't need to compile
       custom kernels as often to help debug issues.

     - bch2_trans_kmalloc() calls can be tracked (there's a new kconfig
       option). With it on you can check the btree_transaction_stats in
       debugfs to see the bch2_trans_kmalloc() calls a transaction did
       when it used the most memory.

* tag 'bcachefs-2025-05-24' of git://evilpiepirate.org/bcachefs: (218 commits)
  bcachefs: Don't mount bs > ps without TRANSPARENT_HUGEPAGE
  bcachefs: Fix btree_iter_next_node() for new locking asserts
  bcachefs: Ensure we don't use a blacklisted journal seq
  bcachefs: Small check_fix_ptr fixes
  bcachefs: Fix opts.recovery_pass_last
  bcachefs: Fix allocate -> self healing path
  bcachefs: Fix endianness in casefold check/repair
  bcachefs: Path must be locked if trans->locked && should_be_locked
  bcachefs: Simplify bch2_path_put()
  bcachefs: Plumb btree_trans for more locking asserts
  bcachefs: Clear trans->locked before unlock
  bcachefs: Clear should_be_locked before unlock in key_cache_drop()
  bcachefs: bch2_path_get() reuses paths if upgrade_fails & !should_be_locked
  bcachefs: Give out new path if upgrade fails
  bcachefs: Fix btree_path_get_locks when not doing trans restart
  bcachefs: btree_node_locked_type_nowrite()
  bcachefs: Kill bch2_path_put_nokeep()
  bcachefs: bch2_journal_write_checksum()
  bcachefs: Reduce stack usage in data_update_index_update()
  bcachefs: bch2_trans_log_str()
  ...
```

## RC2

<details>
<summary>Show merges (1)</summary>

- 2025-06-13: Merge tag 'bcachefs-2025-06-12' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/36df6f734a7ad69880c5262543165c47cb57169f))

```text
Merge tag 'bcachefs-2025-06-12' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-06-12' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "As usual, highlighting the ones users have been noticing:

   - Fix a small issue with has_case_insensitive not being propagated on
     snapshot creation; this led to fsck errors, which we're harmless
     because we're not using this flag yet (it's for overlayfs +
     casefolding).

   - Log the error being corrected in the journal when we're doing fsck
     repair: this was one of the "lessons learned" from the i_nlink 0 ->
     subvolume deletion bug, where reconstructing what had happened by
     analyzing the journal was a bit more difficult than it needed to
     be.

   - Don't schedule btree node scan to run in the superblock: this fixes
     a regression from the 6.16 recovery passes rework, and let to it
     running unnecessarily.

     The real issue here is that we don't have online, "self healing"
     style topology repair yet: topology repair currently has to run
     before we go RW, which means that we may schedule it unnecessarily
     after a transient error. This will be fixed in the future.

   - We now track, in btree node flags, the reason it was scheduled to
     be rewritten. We discovered a deadlock in recovery when many btree
     nodes need to be rewritten because they're degraded: fully fixing
     this will take some work but it's now easier to see what's going
     on.

     For the bug report where this came up, a device had been kicked RO
     due to transient errors: manually setting it back to RW was
     sufficient to allow recovery to succeed.

   - Mark a few more fsck errors as autofix: as a reminder to users,
     please do keep reporting cases where something needs to be repaired
     and is not repaired automatically (i.e. cases where -o fix_errors
     or fsck -y is required).

   - rcu_pending.c now works with PREEMPT_RT

   - 'bcachefs device add', then umount, then remount wasn't working -
     we now emit a uevent so that the new device's new superblock is
     correctly picked up

   - Assorted repair fixes: btree node scan will no longer incorrectly
     update sb->version_min,

   - Assorted syzbot fixes"

* tag 'bcachefs-2025-06-12' of git://evilpiepirate.org/bcachefs: (23 commits)
  bcachefs: Don't trace should_be_locked unless changing
  bcachefs: Ensure that snapshot creation propagates has_case_insensitive
  bcachefs: Print devices we're mounting on multi device filesystems
  bcachefs: Don't trust sb->nr_devices in members_to_text()
  bcachefs: Fix version checks in validate_bset()
  bcachefs: ioctl: avoid stack overflow warning
  bcachefs: Don't pass trans to fsck_err() in gc_accounting_done
  bcachefs: Fix leak in bch2_fs_recovery() error path
  bcachefs: Fix rcu_pending for PREEMPT_RT
  bcachefs: Fix downgrade_table_extra()
  bcachefs: Don't put rhashtable on stack
  bcachefs: Make sure opts.read_only gets propagated back to VFS
  bcachefs: Fix possible console lock involved deadlock
  bcachefs: mark more errors autofix
  bcachefs: Don't persistently run scan_for_btree_nodes
  bcachefs: Read error message now prints if self healing
  bcachefs: Only run 'increase_depth' for keys from btree node csan
  bcachefs: Mark need_discard_freespace_key_bad autofix
  bcachefs: Update /dev/disk/by-uuid on device add
  bcachefs: Add more flags to btree nodes for rewrite reason
  ...
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2025-06-26: Merge tag 'bcachefs-2025-06-26' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/6f2a71a99ebd5dfaa7948a2e9c59eae94b741bd8))

```text
Merge tag 'bcachefs-2025-06-26' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-06-26' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - Lots of small check/repair fixes, primarily in subvol loop and
   directory structure loop (when involving snapshots).

 - Fix a few 6.16 regressions: rare UAF in the foreground allocator path
   when taking a transaction restart from the transaction bump
   allocator, and some small fallout from the change to log the error
   being corrected in the journal when repairing errors, also some
   fallout from the btree node read error logging improvements.

   (Alan, Bharadwaj)

 - New option: journal_rewind

   This lets the entire filesystem be reset to an earlier point in time.

   Note that this is only a disaster recovery tool, and right now there
   are major caveats to using it (discards should be disabled, in
   particular), but it successfully restored the filesystem of one of
   the users who was bit by the subvolume deletion bug and didn't have
   backups. I'll likely be making some changes to the discard path in
   the future to make this a reliable recovery tool.

 - Some new btree iterator tracepoints, for tracking down some
   livelock-ish behaviour we've been seeing in the main data write path.

* tag 'bcachefs-2025-06-26' of git://evilpiepirate.org/bcachefs: (51 commits)
  bcachefs: Plumb correct ip to trans_relock_fail tracepoint
  bcachefs: Ensure we rewind to run recovery passes
  bcachefs: Ensure btree node scan runs before checking for scanned nodes
  bcachefs: btree_root_unreadable_and_scan_found_nothing should not be autofix
  bcachefs: fix bch2_journal_keys_peek_prev_min() underflow
  bcachefs: Use wait_on_allocator() when allocating journal
  bcachefs: Check for bad write buffer key when moving from journal
  bcachefs: Don't unlock the trans if ret doesn't match BCH_ERR_operation_blocked
  bcachefs: Fix range in bch2_lookup_indirect_extent() error path
  bcachefs: fix spurious error_throw
  bcachefs: Add missing bch2_err_class() to fileattr_set()
  bcachefs: Add missing key type checks to check_snapshot_exists()
  bcachefs: Don't log fsck err in the journal if doing repair elsewhere
  bcachefs: Fix *__bch2_trans_subbuf_alloc() error path
  bcachefs: Fix missing newlines before ero
  bcachefs: fix spurious error in read_btree_roots()
  bcachefs: fsck: Fix oops in key_visible_in_snapshot()
  bcachefs: fsck: fix unhandled restart in topology repair
  bcachefs: fsck: Fix check_directory_structure when no check_dirents
  bcachefs: Fix restart handling in btree_node_scrub_work()
  ...
```


</details>

## RC5

<details>
<summary>Show merges (1)</summary>

- 2025-07-04: Merge tag 'bcachefs-2025-07-03' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/482deed9dfa065cf3f68372dadac857541c7d504))

```text
Merge tag 'bcachefs-2025-07-03' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-07-03' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "The 'opts.casefold_disabled' patch is non critical, but would be a
  6.15 backport; it's to address the casefolding + overlayfs
  incompatibility that was discovvered late.

  It's late because I was hoping that this would be addressed on the
  overlayfs side (and will be in 6.17), but user reports keep coming in
  on this one (lots of people are using docker these days)"

* tag 'bcachefs-2025-07-03' of git://evilpiepirate.org/bcachefs:
  bcachefs: opts.casefold_disabled
  bcachefs: Work around deadlock to btree node rewrites in journal replay
  bcachefs: Fix incorrect transaction restart handling
  bcachefs: fix btree_trans_peek_prev_journal()
  bcachefs: mark invalid_btree_id autofix
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2025-07-12: Merge tag 'bcachefs-2025-07-11' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/4412b8b23de24a94a0b78ac283db043c833a3975))

```text
Merge tag 'bcachefs-2025-07-11' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-07-11' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet.

* tag 'bcachefs-2025-07-11' of git://evilpiepirate.org/bcachefs:
  bcachefs: Don't set BCH_FS_error on transaction restart
  bcachefs: Fix additional misalignment in journal space calculations
  bcachefs: Don't schedule non persistent passes persistently
  bcachefs: Fix bch2_btree_transactions_read() synchronization
  bcachefs: btree read retry fixes
  bcachefs: btree node scan no longer uses btree cache
  bcachefs: Tweak btree cache helpers for use by btree node scan
  bcachefs: Fix btree for nonexistent tree depth
  bcachefs: Fix bch2_io_failures_to_text()
  bcachefs: bch2_fpunch_snapshot()
```


</details>

## RC7

<details>
<summary>Show merges (1)</summary>

- 2025-07-18: Merge tag 'bcachefs-2025-07-17' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/d3d16f31d7b305df46080a95f2d254f78e04d588))

```text
Merge tag 'bcachefs-2025-07-17' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-07-17' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - two small syzbot fixes

 - fix discard behaviour regression; we no longer wait until the number
   of buckets needing discard is greater than the number of buckets
   available before kicking off discards

 - fix a fast_list leak when async object debugging is enabled

 - fixes for casefolding when CONFIG_UTF8 != y

* tag 'bcachefs-2025-07-17' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix bch2_maybe_casefold() when CONFIG_UTF8=n
  bcachefs: Fix build when CONFIG_UNICODE=n
  bcachefs: Fix reference to invalid bucket in copygc
  bcachefs: Don't build aux search tree when still repairing node
  bcachefs: Tweak threshold for allocator triggering discards
  bcachefs: Fix triggering of discard by the journal path
  bcachefs: io_read: remove from async obj list in rbio_done()
```


</details>

## final

<details>
<summary>Show merges (1)</summary>

- 2025-07-25: Merge tag 'bcachefs-2025-07-24' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/bef3012b2f6814af2b5c5abd6b5f85921dbb8a01))

```text
Merge tag 'bcachefs-2025-07-24' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-07-24' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "User reported fixes:

   - Fix btree node scan on encrypted filesystems by not using btree
     node header fields encrypted

   - Fix a race in btree write buffer flush; this caused EROs primarily
     during fsck for some people"

* tag 'bcachefs-2025-07-24' of git://evilpiepirate.org/bcachefs:
  bcachefs: Add missing snapshots_seen_add_inorder()
  bcachefs: Fix write buffer flushing from open journal entry
  bcachefs: btree_node_scan: don't re-read before initializing found_btree_node
```


</details>
