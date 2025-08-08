+++
title = "An overview of bcachefs debugging facilities"
slug = "Debugging"
url = "/Developer/Debugging/"
+++

Everything about the internal operation of the system should be easily visible
at runtime, via sysfs, debugfs or tracepoints. If you notice something that
isn't sufficiently visible, please file a bug.

If something goes wonky or is behaving unexpectedly, there should be enough
information readily and easily available at runtime to understand what bcachefs
is doing and why.

Also, when an error occurs, the error message should print out _all_ the
relevant information we have; it should print out enough information for the
issue to be debugged, without hunting for more.

And if something goes really wrong and fsck isn't able to recover, there should
be tooling for working with the developers to get that fixed, too.

## Runtime facilities

For inspection of a running bcachefs filesystem, including questions like "what
is my filesystem doing and why?", we have:

- sysfs: `/sys/fs/bcachefs/<uuid>/`

   Here we've got basic information about the filesystem and member devices.
   There's also an `options` directory which allows filesystem options to be
   set and queried at runtime, a `time_stats` with statistics on various events
   we track latency for, and an `internal` directory with additional debug info.

- debugfs: `/sys/kernel/debug/bcachefs/<uuid>/`

   Debugfs also shows the full contents of every btree - all metadata is a key
   in a btree, so this means all filesystem metadata is inspectable here.
   There's additional per-btree files that show other useful btree information
   (how full are btree nodes, bkey packing statistics, etc.).

- tracepoints and counters

   In addition to the usual tracepoints, we keep persistent counters for every
   tracepoint event, so that it's possible to see if slowpath events have been
   occuring without tracing having been previously enabled.

   `/sys/fs/bcachefs/<uuid>/counters` shows, for every event, the number of
   events since filesystem creation, and since mount.

## Hints on where to get started

Is something spinning? Does the system appear to be trying to get work done,
without getting anything done?

Check `top`: this shows CPU usage by thread - is something spinning?

Check `perf top`: this shows CPU usage, broken out by function/module - what code is spinning?

Check `perf top -e bcachefs:*`: this shows counters for all bcachefs events - are we hitting a rare or slowpath event?

Is everything stuck?

Check `btree_transactions` in debugfs -
`/sys/kernel/debug/bcachefs/<uuid>/btree_transactions`; other files there may
also be relevant.

Is something stuck?

Check sysfs `dev-0/alloc_debug`: this shows various internal allocator state -
perhaps the allocator is stuck?

Something funny with rebalance/background data tasks?

Check sysfs `internal/rebalance_work`, `internal/moving_ctxts`

All of this stuff could use reorganizing and expanding, of course.

## Offline filesystem inspection

The `bcachefs list` subcommand lists the contents of the btrees - extents, inodes, dirents, and more.

The `bcachefs list_journal` subcommand lists the contents of the journal. This
can be used to discover what operation caused an error, e.g. reported by fsck,
by searching for the transaction that last updated those key(s).

### Unrepairable filesystem debugging

If there's an issue that fsck can't fix, use the `bcachefs dump` subcommand,
and then [magic wormhole](https://github.com/magic-wormhole/magic-wormhole),
to send your filesystem metadata to the developers.

## For the developer

Internally, bcachefs uses `printbufs` for formatting text in a generic and
structured way, and we try to write `to_text()` functions for as many types as
possible.

This makes it much easier to write good error messages, and add new debug tools
to sysfs/debugfs; when `to_text()` functions already exist for all the relevant
types, this work is much easier.

Try to keep up with and extend this approach when working with the code.
