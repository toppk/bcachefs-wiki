+++
title = "Btree Nodes"
slug = "BtreeNodes"
url = "/Architecture/BtreeNodes/"
+++

struct btree - an in memory btree node

## Locking

Btree nodes in memory are cached, which means that at any given time if a struct
btree is unlocked it may be evicted from the cache or reused for another btree
node. In general, whenever we lock a btree node we must check after taking the
lock that it is still the btree node we wanted.

A major simplification is that struct btree itself is never freed, except during
shutdown (though the much larger buffers it points to that contain the on disk
btree node may be freed). This means we can drop and retake locks without
needing reference counts.

We aggressively drop and retake locks on btree nodes - locks on btree nodes
should never be held during some other long running operation (e.g. IO). This is
very important for the overall latency of the system.

A single lock is embedded in struct btree, which is a SIX lock -
shared/intent/exclusive. It’s like a read/write lock, but with an extra
intermediate state - intent. Intent locks conflict with other intent locks, but
do not conflict with read locks, and an intent lock must be held before taking a
write lock. Otherwise, they work like normal read/write locks.

The SIX locks also have a sequence number, which is incremented when taking or
releasing a write lock. This is used for dropping and retaking locks: whenever
we have a btree node locked, we record the current sequence number (in struct
btree_iter). Then we can unlock and then retake that lock iff the sequence
number hasn’t changed - if relock succeeds that means our iterator for that
btree node is still valid.

The write lock protects all mutation of struct btree or its contents, with one
major exception - writing a btree node to disk can be done with only a read
lock. For btree node writes, the dirty bit on the btree node provides exclusion
between multiple threads calling `__bch2_btree_node_write()` simultaneously.

Historically, this was required because the update path (in btree_update_leaf.c)
would get a journal reservation with intent locks held on the relevant btree
nodes, but getting a journal reservation may require invoking journal reclaim
and flushing btree nodes, perhaps those same nodes the update had locked. The
current code no longer blocks on getting a journal reservation with btree nodes
locked, though. It’s still desirable to be able to write a btree node with only
a read lock as we can get a read lock with much lower latency than an intent
lock.

Writing a btree node requires updating b->written (the count of how many sectors
in that btree node have been written to disk; btree nodes are log structured);
this means b->written can only be accessed/trusted with a write lock held. This
also means that in the update path we can’t check if a btree node has enough
space for an update or will need to be split until after taking a write lock.

## Lock ordering

A thread may have many btree nodes locked simultaneously; this means we have to
define and adhere to a lock ordering or we’ll have deadlocks. But, code using
and traversing btree iterators can’t be expected to know about this lock
ordering: instead, whenever we lock a btree node we check what other nodes we
have locked (via struct btree_trans and btree_iter) and if we’re violating lock
ordering (and trylock fails) locking the btree node fails - and the btree
transaction must be restarted from the top, where bch2_trans_begin() will
re-traverse all iterators in the correct order.

## Lifecycle

Btree nodes are cached and kept in a hash table; bch2_btree_node_get() will look
up a btree node in the cache and return it locked. Btree roots are the
exception; they are pinned in memory and may be accessed directly via
`c->btree_roots[BTREE_ID].b`.

After locking a btree root (in btree_iter_traverse_one() ->
btree_iter_lock_root()) we must check if that node is still the root node of
that btree - similarly to how in bch2_btree_node_get() after looking up a node
in the hash table and locking it we must check that it is still the node we
wanted.

Btree nodes in the btree cache hash table are indexed by the physical on disk
pointer, not their logical key. This is because btree node split/compact
operations are COW; we allocate new btree node(s), update the parent to point to
the new node(s), and then free the old node - thus we have to add the new btree
nodes to the btree node cache before freeing the old one.
