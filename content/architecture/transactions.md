+++
title = "Transactions"
slug = "Transactions"
url = "/Architecture/Transactions/"
+++

This was originally posted on Patreon, reproduced here for the background on how transactions/atomicity works in bcachefs

So, for some background: every remotely modern filesystem has some sort of
facility for what database people just call transactions - doing complex
operations atomically, so that in the event of a crash the operation either
happened completely or not at all - we're never left in a halfway state.

For example, creating a new file requires doing a few different things:

- allocating a new inode

- creating a new dirent

- when creating a new directory, updating i_nlinks in the parent directory

If you were to crash halfway through, your filesystem is now inconsistent:
you've either got a new inode that doesn't have any dirents pointing to it, or
a dirent that points to a nonexistent inode, and detecting and fixing this
requires a global scan of every inode and dirent in the filesystem. Hence why
older filesystems required fsck after unclean shutdown.

The first journalling filesystems (e.g. ext3) took one approach to solving
this: Essentially, for every complex operation that they want to make atomic,
when they start that operation they first write a description of what they're
about to do to a central log - the journal. E.g. "I'm creating a new file; I
allocated inode number 3487 and I'm going to create a new dirent named foo in
the directory bar". Then, after that description is written to the journal,
they make all the required changes on disk - and once those are complete, they
can write another entry in the journal indicating that the create has been
finished.

But none of the first journalling filesystems were really clean slate designs -
they were all, to greater or lesser extent, bolting journalling onto a
classical Unix filesystem design. As a result, these log entries in the journal
end up getting rather complicated - they're essentially describing, in some
detail, each and every operation a filesystem does that changes its metadata in
some fashion. The code for managing the journal and replaying it on startup
gets to be rather nontrivial too.

There's a wide variety of techniques when it comes to filesystem journalling,
and as a disclaimer I'm not terribly qualified to talk about what other
filesystems do. Btrfs takes a completely different approach - naturally, its
COW btrees are a large part of the story - but it too has grown rather
complicated logging that I'm not at all qualified to talk about.

Bcachefs takes a different approach - I don't know of any other filesystems
that do anything like what bcachefs does, although I wouldn't be surprised if
the techniques I'm using are well known in database land.

Bcachefs currently has no real transactions. There is a journal, but its only
purpose is to log btree updates - it's only used by the btree code, no other
code makes direct use of it. And it doesn't log complex operations - all it
logs are a list of keys to be inserted into the btree: journal replay literally
consists of just re-inserting all the keys in the journal into the btree, in
the same order as they were present in the journal:
<https://evilpiepirate.org/git/linux-bcache.git/tree/drivers/md/bcache/journal.c?h=bcache-dev#n1218>

So then, how does the filesystem do complex operations - like a create or a
rename - atomically?

The first part is that bcachefs has a different design than other filesystems -
you could say that bcachefs the filesystem sits on top of bcache, the key/value
store. Other filesystems may have operations like "Allocate block a new block,
add it to this inode's block map, update the inode's i_size and i_blocks to be
consistent with the new block - oh, and this all has to be ordered correctly
with writing the data to the new block". In bcachefs, every operation is just
one or more keys to be inserted into the various btrees - the extents btree,
the inodes btree, the dirents btree, et cetera. So, at the level of the
filesystem code in bcachefs, the "complex operations" are drastically simpler
than in other filesystems.

So, to do those operations atomically, all we need is the ability to do
multiple btree updates atomically - for example, to append to a file we update
the extents btree with the new extent atomically with updating the inode in the
inodes btree with the new i_size and i_blocks. For a rename, we create the new
dirent atomically with deleting the old dirent (in bcache's btrees, a deletion
is just an insertion of a key with type KEY_TYPE_DELETED - a whiteout - which
overwrites the old key).

For anyone who wants to peruse the code - I wouldn't call it particularly
readable, but bch_btree_insert_trans() is where the magic happens. Here's the
code that handles updating i_size and i_blocks when updating extents:

<https://evilpiepirate.org/git/linux-bcache.git/tree/drivers/md/bcache/fs-io.c?h=bcache-dev#n263>

And rename:

<https://evilpiepirate.org/git/linux-bcache.git/tree/drivers/md/bcache/dirent.c?h=bcache-dev#n190>

The really nice thing about this approach is that we're not logging complex
operations, we're just doing them atomically - so on recovery, that rename or
that append either fully completed or it never happened, we aren't messing with
replaying creates or renames or appends. The journal replay code in bcachefs is
no more complicated than in upstream bcache, it's still just reinserting a list
of keys, one by one. That really is a nontrivial advantage - journal
recovery/log replay code is particularly fiddly to test. That code is not going
to get run and tested nearly as often as the rest of your filesystem code, so
you really want as little of it as possible.

Here's the journal replay code, by the way - note that it's using the normal
btree update interface:

<https://evilpiepirate.org/git/linux-bcache.git/tree/drivers/md/bcache/journal.c?h=bcache-dev#n1218>

Now, the downside: this approach only works for operations that require
updating a small number of keys. That covers all the common, fast path stuff in
a filesystem - if it requires updating many keys, it better not be in your fast
path! But it doesn't quite cover everything.

fcollapse() is a good example. For those who aren't aware of what it does, it
allows you to delete a range in the middle of a file - punching out a hole -
but also shifting all the data above the hole down, so that there's no gap.

Right now, fcollapse() in bcachefs is not atomic. If you crash in the middle of
a collapse operation, your filesystem will be fine - it'll be consistent, and
you won't run into any filesystem errors - but the file you were running
fcollapse() is going to be left somewhere in the middle, with some of the data
shifted down and some not. In other words, corrupted, and not what you wanted.

So, what's the plan?

Well, we can put multiple keys in the same journal entry - that's how the
existing bch_btree_insert_trans() works:

<https://evilpiepirate.org/git/linux-bcache.git/tree/drivers/md/bcache/btree_update.c?h=bcache-dev#n1576>

But, that doesn't mean we can stick arbitrary numbers of keys in the same
journal entry. For one, the journal wasn't designed for it - a journal entry
has to fit in a single journal write, and also while you hold a journal
reservation you block that journal entry from being written; hold it too long
and you'll eventually block other processes from getting new journal
reservations. Also, the journal reservation must be acquired after acquiring
the intent lock on the btree node(s) to be updated - otherwise, updates in the
journal could appear in the wrong order, since the order things appear in the
journal is determined by the order in which the reservations were acquired.

So, we don't want to use the existing journal machinery for this. That's good,
though - it does its job well, and if we tried retrofitting new more
complicated types of transactions onto it we'd be making a lot of core
functionality drastically more complicated.

But note that we do have the ability to update multiple keys in multiple btrees
simultaneously. What if we added a new "transactions" btree? A key in that
btree would correspond to one of our new, heavyweight transactions: as the
operation proceeded, whenever it did some work (updating keys in the various
btrees) it would also update its transaction key with the current state.

Here's the fcollapse() code - notice the main part of it consists of a loop
while it walks all the extents to be moved:

<https://evilpiepirate.org/git/linux-bcache.git/tree/drivers/md/bcache/fs-io.c?h=bcache-dev#n1866>

It should be a relatively straightforward conversion - essentially, all we'd be
doing is taking that function's various local variables that track where it is
as it's looping over the extents and moving them into its transaction key, so
that they also get persisted whenever it does some work.

There's one annoying issue with this approach - one would expect that in
typical filesystem usage, there would be a small number of outstanding
transactions at any given time - so they'll all fit in the same btree node. But
they'll all be updating that same btree node constantly, every time they do a
bit of work - so we'd be introducing quite a bit of lock contention. Ick.

But the keys are never going to be read at runtime - there wouldn't ever be any
reason to do a lookup on any key in BTREE_ID_TRANSACTIONS at runtime - why have
a btree at all?  Why not _only_ store them in the journal?

That's the approach I'm taking. I'm adding a new btree id, but it's just so
that the journal code and bch_btree_insert_trans() can distinguish them - these
new transaction keys will only be persisted in the journal. You can check out
my (in progress, definitely not working yet) code here:

<https://evilpiepirate.org/git/linux-bcache.git/log/?h=bcache-transactions>

Also, my main motivation for working on this wasn't fcollapse() - fcollapse is
just a useful test case for the new approach. The immediate motivation is
actually correctly implementing i_generation for nfs export support: nfs
requires inodes have an i_generation field such that (inode nr, i_generation)
uniquely identifies an inode for the life of a filesystem. But doing that
correctly requires saving some additional state somewhere that we update
atomically with creating a new inode (or else saving a placeholder with the
current i_generation when we delete an inode, and reusing deleted inodes - but
that will have major downsides when using snapshots). Snapshots are also going
to require this new transaction machinery, but that's quite a ways off.
