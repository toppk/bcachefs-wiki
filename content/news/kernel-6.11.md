+++
title = "Linux 6.11: bcachefs merges"
date = 2024-09-09T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.11.

## RC1

- 2024-07-22: Merge tag 'bcachefs-2024-07-22' of https://evilpiepirate.org/git/bcachefs ([commit](https://git.kernel.org/torvalds/c/dd018c238b8489b6dd8c06f6b962ea75d79115ff))

```text
Merge tag 'bcachefs-2024-07-22' of https://evilpiepirate.org/git/bcachefs

Merge tag 'bcachefs-2024-07-22' of https://evilpiepirate.org/git/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - another fix for fsck getting stuck, from marcin

 - small syzbot fix

 - another undefined shift fix

* tag 'bcachefs-2024-07-22' of https://evilpiepirate.org/git/bcachefs:
  bcachefs: Fix printbuf usage while atomic
  bcachefs: More informative error message in reattach_inode()
  bcachefs: kill btree_trans_too_many_iters() in bch2_bucket_alloc_freelist()
  bcachefs: mean_and_variance: Avoid too-large shift amounts
```

## RC3

<details>
<summary>Show merges (2)</summary>

- 2024-08-10: Merge tag 'bcachefs-2024-08-10' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/31b244460634c74430745a74e56f5c88c43f079b))

```text
Merge tag 'bcachefs-2024-08-10' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-08-10' of git://evilpiepirate.org/bcachefs

Pull more bcachefs fixes from Kent Overstreet:
 "A couple last minute fixes for the new disk accounting

   - fix a bug that was causing ACLs to seemingly "disappear"

   - new on disk format version, bcachefs_metadata_version_disk_accounting_v3

     bcachefs_metadata_version_disk_accounting_v2 accidentally included
     padding in disk_accounting_key; fortunately, 6.11 isn't out yet so
     we can fix this with another version bump"

* tag 'bcachefs-2024-08-10' of git://evilpiepirate.org/bcachefs:
  bcachefs: bcachefs_metadata_version_disk_accounting_v3
  bcachefs: improve bch2_dev_usage_to_text()
  bcachefs: bch2_accounting_invalid()
  bcachefs: Switch to .get_inode_acl()
```

- 2024-08-08: Merge tag 'bcachefs-2024-08-08' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/b3f5620f76f9a6da024bd243a73fa8e2df520c5a))

```text
Merge tag 'bcachefs-2024-08-08' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-08-08' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Assorted little stuff:

   - lockdep fixup for lockdep_set_notrack_class()

   - we can now remove a device when using erasure coding without
     deadlocking, though we still hit other issues

   - the 'allocator stuck' timeout is now configurable, and messages are
     ratelimited. The default timeout has been increased from 10 seconds
     to 30"

* tag 'bcachefs-2024-08-08' of git://evilpiepirate.org/bcachefs:
  bcachefs: Use bch2_wait_on_allocator() in btree node alloc path
  bcachefs: Make allocator stuck timeout configurable, ratelimit messages
  bcachefs: Add missing path_traverse() to btree_iter_next_node()
  bcachefs: ec should not allocate from ro devs
  bcachefs: Improved allocator debugging for ec
  bcachefs: Add missing bch2_trans_begin() call
  bcachefs: Add a comment for bucket helper types
  bcachefs: Don't rely on implicit unsigned -> signed integer conversion
  lockdep: Fix lockdep_set_notrack_class() for CONFIG_LOCK_STAT
  bcachefs: Fix double free of ca->buckets_nouse
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2024-08-17: Merge tag 'bcachefs-2024-08-16' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/b71817585383d96ddc51ebd126f6253fdb9a8568))

```text
Merge tag 'bcachefs-2024-08-16' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-08-16' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent OverstreetL

 - New on disk format version, bcachefs_metadata_version_disk_accounting_inum

   This adds one more disk accounting counter, which counts disk usage
   and number of extents per inode number. This lets us track
   fragmentation, for implementing defragmentation later, and it also
   counts disk usage per inode in all snapshots, which will be a useful
   thing to expose to users.

 - One performance issue we've observed is threads spinning when they
   should be waiting for dirty keys in the key cache to be flushed by
   journal reclaim, so we now have hysteresis for the waiting thread, as
   well as improving the tracepoint and a new time_stat, for tracking
   time blocked waiting on key cache flushing.

... and various assorted smaller fixes.

* tag 'bcachefs-2024-08-16' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix locking in __bch2_trans_mark_dev_sb()
  bcachefs: fix incorrect i_state usage
  bcachefs: avoid overflowing LRU_TIME_BITS for cached data lru
  bcachefs: Fix forgetting to pass trans to fsck_err()
  bcachefs: Increase size of cuckoo hash table on too many rehashes
  bcachefs: bcachefs_metadata_version_disk_accounting_inum
  bcachefs: Kill __bch2_accounting_mem_mod()
  bcachefs: Make bkey_fsck_err() a wrapper around fsck_err()
  bcachefs: Fix warning in __bch2_fsck_err() for trans not passed in
  bcachefs: Add a time_stat for blocked on key cache flush
  bcachefs: Improve trans_blocked_journal_reclaim tracepoint
  bcachefs: Add hysteresis to waiting on btree key cache flush
  lib/generic-radix-tree.c: Fix rare race in __genradix_ptr_alloc()
  bcachefs: Convert for_each_btree_node() to lockrestart_do()
  bcachefs: Add missing downgrade table entry
  bcachefs: disk accounting: ignore unknown types
  bcachefs: bch2_accounting_invalid() fixup
  bcachefs: Fix bch2_trigger_alloc when upgrading from old versions
  bcachefs: delete faulty fastpath in bch2_btree_path_traverse_cached()
```


</details>

## RC5

<details>
<summary>Show merges (1)</summary>

- 2024-08-25: Merge tag 'bcachefs-2024-08-24' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/72bea05cb1ad486b1a850f584cc93b651579ad2f))

```text
Merge tag 'bcachefs-2024-08-24' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-08-24' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - assorted syzbot fixes

 - some upgrade fixes for old (pre 1.0) filesystems

 - fix for moving data off a device that was switched to durability=0
   after data had been written to it.

 - nocow deadlock fix

 - fix for new rebalance_work accounting

* tag 'bcachefs-2024-08-24' of git://evilpiepirate.org/bcachefs: (28 commits)
  bcachefs: Fix rebalance_work accounting
  bcachefs: Fix failure to flush moves before sleeping in copygc
  bcachefs: don't use rht_bucket() in btree_key_cache_scan()
  bcachefs: add missing inode_walker_exit()
  bcachefs: clear path->should_be_locked in bch2_btree_key_cache_drop()
  bcachefs: Fix double assignment in check_dirent_to_subvol()
  bcachefs: Fix refcounting in discard path
  bcachefs: Fix compat issue with old alloc_v4 keys
  bcachefs: Fix warning in bch2_fs_journal_stop()
  fs/super.c: improve get_tree() error message
  bcachefs: Fix missing validation in bch2_sb_journal_v2_validate()
  bcachefs: Fix replay_now_at() assert
  bcachefs: Fix locking in bch2_ioc_setlabel()
  bcachefs: fix failure to relock in btree_node_fill()
  bcachefs: fix failure to relock in bch2_btree_node_mem_alloc()
  bcachefs: unlock_long() before resort in journal replay
  bcachefs: fix missing bch2_err_str()
  bcachefs: fix time_stats_to_text()
  bcachefs: Fix bch2_bucket_gens_init()
  bcachefs: Fix bch2_trigger_alloc assert
  ...
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2024-09-01: Merge tag 'bcachefs-2024-08-21' of https://github.com/koverstreet/bcachefs ([commit](https://git.kernel.org/torvalds/c/a4c763129fbcc7da5d3134ea95f9577f25bc637d))

```text
Merge tag 'bcachefs-2024-08-21' of https://github.com/koverstreet/bcachefs

Merge tag 'bcachefs-2024-08-21' of https://github.com/koverstreet/bcachefs

Push bcachefs fixes from Kent Overstreet:
 "The data corruption in the buffered write path is troubling; inode
  lock should not have been able to cause that...

   - Fix a rare data corruption in the rebalance path, caught as a nonce
     inconsistency on encrypted filesystems

   - Revert lockless buffered write path

   - Mark more errors as autofix"

* tag 'bcachefs-2024-08-21' of https://github.com/koverstreet/bcachefs:
  bcachefs: Mark more errors as autofix
  bcachefs: Revert lockless buffered IO path
  bcachefs: Fix bch2_extents_match() false positive
  bcachefs: Fix failure to return error in data_update_index_update()
```


</details>

## RC7

<details>
<summary>Show merges (1)</summary>

- 2024-09-04: Merge tag 'bcachefs-2024-09-04' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/c763c43396883456ef57e5e78b64d3c259c4babc))

```text
Merge tag 'bcachefs-2024-09-04' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-09-04' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - Fix a typo in the rebalance accounting changes

 - BCH_SB_MEMBER_INVALID: small on disk format feature which will be
   needed for full erasure coding support; this is only the minimum so
   that 6.11 can handle future versions without barfing.

* tag 'bcachefs-2024-09-04' of git://evilpiepirate.org/bcachefs:
  bcachefs: BCH_SB_MEMBER_INVALID
  bcachefs: fix rebalance accounting
```


</details>

## final

<details>
<summary>Show merges (1)</summary>

- 2024-09-09: Merge tag 'bcachefs-2024-09-09' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/bc83b4d1f08695e85e85d36f7b803da58010161d))

```text
Merge tag 'bcachefs-2024-09-09' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2024-09-09' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - fix ca->io_ref usage; analagous to previous patch doing that for main
   discard path

 - cond_resched() in __journal_keys_sort(), cutting down on "hung task"
   warnings when journal is big

 - rest of basic BCH_SB_MEMBER_INVALID support

 - and the critical one: don't delete open files in online fsck, this
   was causing the "dirent points to inode that doesn't point back"
   inconsistencies some users were seeing

* tag 'bcachefs-2024-09-09' of git://evilpiepirate.org/bcachefs:
  bcachefs: Don't delete open files in online fsck
  bcachefs: fix btree_key_cache sysfs knob
  bcachefs: More BCH_SB_MEMBER_INVALID support
  bcachefs: Simplify bch2_bkey_drop_ptrs()
  bcachefs: Add a cond_resched() to __journal_keys_sort()
  bcachefs: Fix ca->io_ref usage
```


</details>
