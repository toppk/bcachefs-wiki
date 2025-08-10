+++
title = "Linux 6.14: bcachefs merges"
date = 2025-03-14T00:00:00Z
+++

This post summarizes bcachefs merges that landed in Linux 6.14.

## RC1

- 2025-01-30: Merge tag 'bcachefs-2025-01-29' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/8080ff5ac656b9ca6c282e4044be19d2b8a837df))

```text
Merge tag 'bcachefs-2025-01-29' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-01-29' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - second half of a fix for a bug that'd been causing oopses on
   filesystems using snapshots with memory pressure (key cache fills for
   snaphots btrees are tricky)

 - build fix for strange compiler configurations that double stack frame
   size

 - "journal stuck timeout" now takes into account device latency: this
   fixes some spurious warnings, and the main remaining source of SRCU
   lock hold time warnings (I'm no longer seeing this in my CI, so any
   users still seeing this should definitely ping me)

 - fix for slow/hanging unmounts (" Improve journal pin flushing")

 - some more tracepoint fixes/improvements, to chase down the "rebalance
   isn't making progress" issues

* tag 'bcachefs-2025-01-29' of git://evilpiepirate.org/bcachefs:
  bcachefs: Improve trace_move_extent_finish
  bcachefs: Fix trace_copygc
  bcachefs: Journal writes are now IOPRIO_CLASS_RT
  bcachefs: Improve journal pin flushing
  bcachefs: fix bch2_btree_node_flags
  bcachefs: rebalance, copygc enabled are runtime opts
  bcachefs: Improve decompression error messages
  bcachefs: bset_blacklisted_journal_seq is now AUTOFIX
  bcachefs: "Journal stuck" timeout now takes into account device latency
  bcachefs: Reduce stack frame size of __bch2_str_hash_check_key()
  bcachefs: Fix btree_trans_peek_key_cache()
```

## RC3

<details>
<summary>Show merges (1)</summary>

- 2025-02-13: Merge tag 'bcachefs-2025-02-12' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/1854c7f79dcaaba9f1c0b131445ace03f9fd532d))

```text
Merge tag 'bcachefs-2025-02-12' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-02-12' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Just small stuff.

  As a general announcement, on disk format is now frozen in my master
  branch - future on disk format changes will be optional, not required.

   - More fixes for going read-only: the previous fix was insufficient,
     but with more work on ordering journal reclaim flushing (and a
     btree node accounting fix so we don't split until we have to) the
     tiering_replication test now consistently goes read-only in less
     than a second.

   - fix for fsck when we have reflink pointers to missing indirect
     extents

   - some transaction restart handling fixes from Alan; the "Pass
     _orig_restart_count to trans_was_restarted" likely fixes some rare
     undefined behaviour heisenbugs"

* tag 'bcachefs-2025-02-12' of git://evilpiepirate.org/bcachefs:
  bcachefs: Reuse transaction
  bcachefs: Pass _orig_restart_count to trans_was_restarted
  bcachefs: CONFIG_BCACHEFS_INJECT_TRANSACTION_RESTARTS
  bcachefs: Fix want_new_bset() so we write until the end of the btree node
  bcachefs: Split out journal pins by btree level
  bcachefs: Fix use after free
  bcachefs: Fix marking reflink pointers to missing indirect extents
```


</details>

## RC4

<details>
<summary>Show merges (1)</summary>

- 2025-02-20: Merge tag 'bcachefs-2025-02-20' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/bf0e5ed0082ef0dbaa43c0296b045d6d9832082e))

```text
Merge tag 'bcachefs-2025-02-20' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-02-20' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Small stuff:

   - The fsck code for Hongbo's directory i_size patch was wrong, caught
     by transaction restart injection: we now have the CI running
     another test variant with restart injection enabled

   - Another fixup for reflink pointers to missing indirect extents:
     previous fix was for fsck code, this fixes the normal runtime paths

   - Another small srcu lock hold time fix, reported by jpsollie"

* tag 'bcachefs-2025-02-20' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix srcu lock warning in btree_update_nodes_written()
  bcachefs: Fix bch2_indirect_extent_missing_error()
  bcachefs: Fix fsck directory i_size checking
```


</details>

## RC5

<details>
<summary>Show merges (1)</summary>

- 2025-02-26: Merge tag 'bcachefs-2025-02-26' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/dd83757f6e686a2188997cb58b5975f744bb7786))

```text
Merge tag 'bcachefs-2025-02-26' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-02-26' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "A couple small ones, the main user visible changes/fixes are:

   - Fix a bug where truncate would rarely fail and return 1

   - Revert the directory i_size code: this turned out to have a number
     of issues that weren't noticed because the fsck code wasn't
     correctly reporting errors (ouch), and we're late enough in the
     cycle that it can just wait until 6.15"

* tag 'bcachefs-2025-02-26' of git://evilpiepirate.org/bcachefs:
  bcachefs: Fix truncate sometimes failing and returning 1
  bcachefs: Fix deadlock
  bcachefs: Check for -BCH_ERR_open_buckets_empty in journal resize
  bcachefs: Revert directory i_size
  bcachefs: fix bch2_extent_ptr_eq()
  bcachefs: Fix memmove when move keys down
  bcachefs: print op->nonce on data update inconsistency
```


</details>

## RC6

<details>
<summary>Show merges (1)</summary>

- 2025-03-06: Merge tag 'bcachefs-2025-03-06' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/0f52fd4f67c67f7f2ea3063c627e466255f027fd))

```text
Merge tag 'bcachefs-2025-03-06' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-03-06' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:

 - Fix a compatibility issue: we shouldn't be setting incompat feature
   bits unless explicitly requested

 - Fix another bug where the journal alloc/resize path could spuriously
   fail with -BCH_ERR_open_buckets_empty

 - Copygc shouldn't run on read-only devices: fragmentation isn't an
   issue if we're not currently writing to a given device, and it may
   not have anywhere to move the data to

* tag 'bcachefs-2025-03-06' of git://evilpiepirate.org/bcachefs:
  bcachefs: copygc now skips non-rw devices
  bcachefs: Fix bch2_dev_journal_alloc() spuriously failing
  bcachefs: Don't set BCH_FEATURE_incompat_version_field unless requested
```


</details>

## RC7

<details>
<summary>Show merges (2)</summary>

- 2025-03-14: Merge tag 'bcachefs-2025-03-14' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/912ad8b317fafbb5a08fc0d9c23cf46af39ec2a7))

```text
Merge tag 'bcachefs-2025-03-14' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-03-14' of git://evilpiepirate.org/bcachefs

Pull bcachefs hotfix from Kent Overstreet:
 "This one is high priority: a user hit an assertion in the upgrade to
  6.14, and we don't have a reproducer, so this changes the assertion to
  an emergency read-only with more info so we can debug it"

* tag 'bcachefs-2025-03-14' of git://evilpiepirate.org/bcachefs:
  bcachefs: Change btree wb assert to runtime error
```

- 2025-03-13: Merge tag 'bcachefs-2025-03-13' of git://evilpiepirate.org/bcachefs ([commit](https://git.kernel.org/torvalds/c/131c040bbb0f561ef68ad2ba6fcd28c97fa6d4cf))

```text
Merge tag 'bcachefs-2025-03-13' of git://evilpiepirate.org/bcachefs

Merge tag 'bcachefs-2025-03-13' of git://evilpiepirate.org/bcachefs

Pull bcachefs fixes from Kent Overstreet:
 "Roxana caught an unitialized value that might explain some of the
  rebalance weirdness we're still tracking down - cool.

  Otherwise pretty minor"

* tag 'bcachefs-2025-03-13' of git://evilpiepirate.org/bcachefs:
  bcachefs: bch2_get_random_u64_below()
  bcachefs: target_congested -> get_random_u32_below()
  bcachefs: fix tiny leak in bch2_dev_add()
  bcachefs: Make sure trans is unlocked when submitting read IO
  bcachefs: Initialize from_inode members for bch_io_opts
  bcachefs: Fix b->written overflow
```


</details>
