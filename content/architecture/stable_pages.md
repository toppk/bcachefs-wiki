---
title: "Stable pages"
slug: "StablePages"
url: "/Architecture/StablePages/"
---

Killian De Volder (Qantourisc) and I ended up having a long discussion about TCQ
vs. write caching, stable pages, and other random stuff about the Linux IO
stack - none of it bcachefs specific, but we thought it might be useful and/or
interesting enough to be worth dumping into the wiki and possibly cleaning up
later.

IRC conversation is reproduced below:

```text
> <Qantourisc> http://brad.livejournal.com/2116715.html

> <Qantourisc> drkshadow: sidenode: I think I will write a custom tool, to test this, that is less complicated to run

> <Qantourisc> as one can use math, to verify the consistency of a file

> <py1hon> heh

> <py1hon> that stuff is a pain

> <Qantourisc> py1hon: what stuff ?

> <py1hon> making sure syncs are passed down correctly

> <Qantourisc> py1hon: the writing the tool, or dealing with that shitstorm of cache-lies ?

> <py1hon> i spotted a bug (hope it's fixed now...) in the DIO code - with O_DIRECT|O_SYNC aio the sync just wasn't happening

> <Qantourisc> py1hon: i'd like to know what setups / disks work ... I run everything with write-cache off, it's painfull

> <py1hon> i mean finding/testing every possible way code can fuck up

> <py1hon> you read enough code you see scary shit

> <Qantourisc> py1hon: ... still ?

> <py1hon> i haven't checked

> <Qantourisc> reminds me 2006 and lvm

> <py1hon> really don't want to :p

> <Qantourisc> "ow now we handle syncs"

> <py1hon> i have enough bugs i'm responsible for thank you very much

> <Qantourisc> i was like ... whaaaat ?

> <py1hon> hah

> <py1hon> yeaaaa

> <Qantourisc> so I run all my servers in direct IO :/

> <py1hon> i think that guy's TCQ thing is a red herring though

> <Qantourisc> TCQ is just another form of cache handeling

> <py1hon> the trouble with the TCQ/barrier model is that it's utterly insane trying to preserve ordering all the way up and down the io stack

> <py1hon> thus

> <Qantourisc> py1hon: i'm just VERRY confused why handeling sync in kernel is so hard

> <py1hon> software ends up being coded to just use explicit flushes

> <py1hon> Qantourisc: i think mostly it's becuase a lot of storage developers rode in on the short bus

> <Qantourisc> "short bus" ?

> <py1hon> yes

> <Qantourisc> what's that ?

> <py1hon> the bus you ride to school if you have "special needs"

> <Qantourisc> ugh

> <Qantourisc> imo, each bio request should return AFTER the write is DONE

> <Qantourisc> OR

> <Qantourisc> return a promise

> <py1hon> in an ideal world yea

> <py1hon> the trouble is

> <py1hon> write caching is really useful

> <Qantourisc> how any other is allowed, I do no understand, me eyeballs linus

> <py1hon> the reason is

> <py1hon> until the write completes

> <Qantourisc> that's what the promises are for

> <py1hon> that memory buffer - you can't touch it

> <Qantourisc> and when you request a sync, you wait until they are all completed (imo)

> <Qantourisc> but yes it's some work

> <py1hon> hold on i'm explaining :P

> <py1hon> so this comes up most notably with the page cache

> <py1hon> also "stable pages" was still a clusterfuck last i checked

> <py1hon> but it'd be even worse without write caching

> <py1hon> so

> <py1hon> if you're a filesystem that cares about data and checksums crap

> <py1hon> you checksum the data you're writing, and then the data you're writing better goddamn not change until the write completes - say userspace is changing it, because that's what they do

> <py1hon> or if it does, your checksum is invalid

> <py1hon> which means:

> <py1hon> to write some data that's cached in the page cache, and mapped into potentially multiple userspace processes

> Qantourisc makes a notes: if userspace writes, just update checksum, or are they writing in the buffer you are about to write  ?

> <py1hon> you have to mark those page table entries RO, flush tlbs etc. etc. so that userspace can't modify that crap

> <py1hon> if userspace modifies the buffer while the write is in flight

> <py1hon> you don't know if the old or the new version was the one that got written

> <py1hon> it's a race

> <py1hon> you're fucked

> <Qantourisc> ... imo once you submit to the kernel what you will write: it's hands off

> <Qantourisc> quess they wanted to prevent an extra page copy

> <py1hon> ignore direct io for now (that has its own issues though)

> <py1hon> yes, that extra copy is bad

> <Qantourisc> py1hon: so is screwing up your data  :)

> <py1hon> not _that_ bad, that's actually what bcachefs does

> <py1hon> but it's a shitty situation

> <py1hon> also having to allocate memory to copy data jsut so you can do io, that's also not a great situation

> <Qantourisc> screwing up data < extra memory copy

> <py1hon> there are lots of good reasons why you don't want to bounce data you're writing if you don't have to

> <py1hon> and mostly, you don't have to

> <py1hon> anyways

> <Qantourisc> Also what wrong with doing "fu" userspace ?

> <Qantourisc> don't do it wrong ?

> <Qantourisc> or is the writing to it' "allowed" ?

> <py1hon> like i said bcachefs is just copying the data

> <py1hon> which i'm sure someone is going to complain about eventually

> <py1hon> sigh

> <py1hon> so getting back to the tcq vs write caching thing

> <py1hon> fundamental issue is, while a write is outstanding the device owns that buffer, you can't touch it or reuse it for anything else

> <Qantourisc> py1hon: then you reply: "I am sorry the current design of what is allowed in the kernel API is to liberal, I can't write out the data you can constantly modify while i'm writing. Complain to Linus to fick this braindead design."

> <py1hon> if doing a write is fast, because writes are cached, this isn't a huge deal

> <py1hon> you can just wait until the write completes, and (potentially) avoid having to bounce

> <Qantourisc> py1hon: quick break "bounce" ?

> <py1hon> bounce = allocate a bounce buffer, copy data into bounce buffer, write using bounce buffer instead of original buffer

> <Qantourisc> a ok

> <Qantourisc> "copy page" in a sence

> <py1hon> if doing a write is slow, because it's always waiting for the device to physically make it persistent

> <py1hon> then, you're probably going to end up bouncing all the writes on the host - introducing an extra copy

> <py1hon> but

> <py1hon> this is stupid

> <py1hon> because the writes are gonna get copied to the device's buffer regardless, so it can do the actual io

> <py1hon> so if you have to copy the data to the device's buffer anyways

> <Qantourisc> sound logical, everyone who promises to write something out later, should copy the data 

> <py1hon> just do that INSTEAD of bouncing

> <py1hon> boom, done

> <py1hon> except not really, there's shitty tradeoffs all around

> <Qantourisc> why are they favoring speed over safety ?

> <py1hon> anyways, there's really no good answers to the bouncing and tcq vs write buffering stuff

> <py1hon> well they're not these days

> <py1hon> excepting bugs of course

> <Qantourisc> so they bounce more then ?

> <py1hon> no you don't want to know about the bouncing situation

> <py1hon> pretend i didn't bring that up because then i'd have to talk about stable pages and like i said that's another bag of shit

> <py1hon> anywys

> <py1hon> userspace has no concept of tcq

> <py1hon> or when a write hits the device

> <py1hon> or what

> <py1hon> all userspace has is fsync and O_SYNC

> <py1hon> and that's _fine_

> <py1hon> those interfaces are completely adequate in practice

> <py1hon> the kernel just has to make sure it actually honors them, which (again, excluding bugs), it does these days

> <Qantourisc> so who could write in the write-page then (in the earlier example with the checksum) ?

> <py1hon> whether it honors fsync and O_SYNC by using flushes or by using TCQ doesn't matter one damn to userspace

> <py1hon> ok, so you mmap a file

> <Qantourisc> agreed, f/Osync is enough

> <py1hon> how's that work?

> <py1hon> or say multiple processes mmap the same file

> <py1hon> MAP_SHARED

> <Qantourisc> py1hon: the only way I see this working: cow

> <py1hon> no

> <py1hon> that would be MAP_PRIVATE

> <py1hon> say they're all writing to the file

> <py1hon> so all their changes, via the mmap() mapping, have to be written out to disk (and also seen by each other blah blah)

> <Qantourisc> sec first, mmap works by pages correct ? and those pages are backed by FS ?

> <py1hon> yes

> <py1hon> and yes

> <py1hon> so that file is cached in the page cache

> <Qantourisc> hold on constructing mental model

> <py1hon> it's cached just once

> <py1hon> then

> <py1hon> every time a process calls mmap()

> <Qantourisc> py1hon: does the kernel know when one has written to a page ?

> <py1hon> the kernel maps those same physical pages to locations in that process's address space by setting up page table entries and mappings and all that crap

> <py1hon> yes

> <py1hon> with help from the CPU

> <Qantourisc> a nice way :)

> <py1hon> page starts out clean, right?

> <Qantourisc> yap

> <py1hon> so when the kernel maps that clean page into the userspace's address space, it maps it read only

> <py1hon> REGARDLESS of whether userspace wants read write access or not

> <py1hon> then, when userspace writes to it, it traps

> <py1hon> SIGBUS, except not, because the kernel sees what was going on

> <py1hon> kernel switches it to read write, notes the page is now dirty, and continues on like nothing ever happened

> <Qantourisc> but how does it detect a second write ?

> <py1hon> doesn't need to

> <py1hon> all it needs to know is that the page is now dirty

> <py1hon> and, at some point in the future, has to be written

> <Qantourisc> ow right, if you want to write it, lock it again first ?

> <py1hon> make it read only, write it, mark it clean

> <py1hon> userspace writes again, cycle repeats

> <Qantourisc> clean == RO map ?

> <py1hon> yea

> <Qantourisc> or a bitmap somewhere ?

> <py1hon> bit in struct page

> <py1hon> however: that was all a lie

> <py1hon> that's how it works conceptually

> <Qantourisc> ok who has cut corners, and why :(

> <py1hon> but, dirtying pages and crap like that is important enough that CPUs actually track this stuff for you without you having to map pages read only and having userspace go to the trouble of faulting

> <py1hon> the end result is, the kernel can just check the page table entries that it sets up for the CPU to see if userspace has written to them

> <Qantourisc> ok we can detect this differently, sound nice, and it blows up in our face  how ?

> <py1hon> (this actually isn't 100% my area, i would be reading docs to check the details on this stuff if i cared)

> <py1hon> ok so, nice thing about this is

> <Qantourisc> no more traps :)

> <py1hon> pages are never read only! userspace can always write to them!

> <py1hon> yes, no more traps!

> <py1hon> (aka, minor faults)

> <py1hon> annoying side effect:

> <py1hon> if pages are never read only...

> <py1hon> userspace can KEEP WRITING TO THEM WHILE THEY'RE BEING WRITTEN

> <py1hon> remember

> <py1hon> if we're not bouncing

> <py1hon> and we don't want to bounce if we don't have to, so usually we don't

> <Qantourisc> .... so why are they not marked RO ?

> <py1hon> the buffer we're writing out is literally the same buffer that is mapped into userspace

> <py1hon> because if they were marked RO, userspace would trap and things would be slow

> <py1hon> now

> <Qantourisc> py1hon: i'd argue it would NOT be slow

> <py1hon> oh i'll get to that

> <Qantourisc> either things are going bad: we are race-condition writing

> <py1hon> this is where it starts to get hilarious

> <py1hon> no not yet

> <Qantourisc> and slow is "ok"

> <py1hon> this is how it worked for many years

> <py1hon> and it worked fine

> <py1hon> reason is

> <Qantourisc> or things are not race-ing and it should be fine

> <py1hon> if there's a write in flight

> <py1hon> and userspace is scribbling over that buffer with new data

> <py1hon> who cares? we're going to overwrite that write with the new version later

> <py1hon> it got marked dirty again

> <Qantourisc> there is ofcours 1 asset of mmap files: write order not garnteed

> <py1hon> if userspace cares about _which specific version_ gets written, they need to stop scribbling over stuff and call fsync()

> <Qantourisc> if one looks at this api

> <py1hon> no really, trust me, this actually does work completely fine

> <py1hon> no data integrity is broken

> <Qantourisc> py1hon: with fsync it works too yes

> <Qantourisc> but if the app refuses to wait: not a clue what version you will get

> <py1hon> yes but that's fine!

> <py1hon> if the app isn't doing an fsync, it CANNOT care

> <Qantourisc> PS: mind if I publish this conversation ? :)

> <py1hon> go for it

> <Qantourisc> verry informative

> <Qantourisc> Might rewrite it later as a doc :p

> <py1hon> i want to emphasize that this approach REALLY IS COMPLETELY OK

> <py1hon> that is

> <py1hon> here's the hilarious part

> <py1hon> UNTIL THE FILESYSTEM STARTS CHECKSUMMING DATA

> Qantourisc ponders

> <py1hon> that is literally the ONLY THING throwing a giant monkey wrench into this approach

> <py1hon> and it's fucking stupid, but it's where we are

> <Qantourisc> py1hon: ... there is a fix I think

> <py1hon> remember: if the filesystem is checksumming the data, then the FILESYSTEM damn well cares about which version gets written because it has to push down the correct checksum

> <Qantourisc> but I don't know if it's allowed

> <py1hon> but if userspace is scribbling over the data underneath everyone... oh fuck

> <Qantourisc> don't write until you get a fsync

> <py1hon> no that doesn't work, for a variety of reasons

> <Qantourisc> performance will however be ... mwea

> <py1hon> there really isn't a good solution

> <py1hon> so

> <Qantourisc> bounce is also a way

> <py1hon> yes, but

> <py1hon> if your solution is bouncing, then you have to preemptively bounce _everything_

> <py1hon> which is stupid

> <Qantourisc> py1hon: just the dirty pages no ?

> <py1hon> i mean every single write you do from the page cache you have to bounce

> <Qantourisc> well you need a copy you can trust

> <py1hon> well

> <Qantourisc> end of story :/

> <py1hon> there's an alternative

> <Qantourisc> I missed one ?

> <py1hon> we talked about it earlier

> Qantourisc feels inferior

> <py1hon> you flip the pages to RO in userspace's mapping

> <py1hon> just until the write completes

> <Qantourisc> but ?

> <Qantourisc> (other then extra work)

> <py1hon> yeah

> <py1hon> should be fine, right? i mean, we're not writing that many pages at once at any given time

> <py1hon> writes are fast because most devices cache writes

> <py1hon> what could go wrong?

> <Qantourisc> write order, diks lie

> <Qantourisc> power loss

> <py1hon> no

> <py1hon> we're only talking about flipping pages to RO in userspace for the duration of the write to avoid having to bounce them

> <py1hon> nothing else changes

> <py1hon> if app does fsync, we still issue a cache flush

> <Qantourisc> looks fine, I missed anything ?

> <py1hon> devices USUALLY don't lie about cache flushes in the past 10-20 years because people get very angry if they do

> <Qantourisc> py1hon: PRO users get angry

> <Qantourisc> desktop users ... myabe

> <py1hon> i know but enterprise storage people are fucking morons

> <py1hon> trust me

> <py1hon> you don't even want to know

> <Qantourisc> py1hon: i've seen my own morons

> <py1hon> i know

> <Qantourisc> they had 2 sans

> <py1hon> and they're morons too

> <py1hon> but dear god fuck enterprise storage

> <Qantourisc> they where syncing 2 raids between 2 sans

> <Qantourisc> 1 whas a RAID5 and the other RAID10

> <py1hon> so, stable pages:

> <Qantourisc> and I was like ... guys ... this stack probably doesn't return writes are complete until all raids have hit the platter

> <Qantourisc> ... downloaded the docs, of the san, and it was true

> <py1hon> year or so back, they did that for stable pages, flipping them RO in the userspace mappings

> <Qantourisc> SAN admin ...; ooow ...euu ... dang

> <py1hon> btrfs needs stable pages for checksums

> <py1hon> other stuff in the io stack would like stable pages

> <py1hon> it was regarded as generally a good idea

> <Qantourisc> stable page == page you can trust userspace will not modify (without you knowing)

> <py1hon> so this was pushed out

> <py1hon> yes

> <py1hon> trouble is, after it was released

> <py1hon> someone came up with a benchmark that got like 200x slower

> <Qantourisc> py1hon: writing to the same page ?

> <py1hon> yeah, just because of userspace having to wait if they tried to write to a page that was being written out

> <Qantourisc> The correct reply would then be "We are sorry, we cannot garantee this without messing up your data, or we bounce"

> <py1hon> and if you think about it

> <py1hon> userspace having to block on IO

> <py1hon> when all it's trying to do is change something in memory

> <py1hon> that is kinda stupid

> <py1hon> and adding latency like that actually is a shitty thing to do because then someone is going to have to debug a horrific latency bug years later and be really pissed when they figure out what it was

> <Qantourisc> Well, there are 2 options here

> <Qantourisc> wait no option

> <py1hon> bouncing

> <py1hon> today, it's pretty much just bouncing

> <py1hon> now, what we COULD do, in THEORY

> <Qantourisc> why is bouncing sooo bad ?

> <py1hon> it's not that bouncing is bad, exactly

> <py1hon> it's that bouncing EVERY SINGLE FUCKING WRITE when 99% of them won't be modified is retarded

> <Qantourisc> py1hon: you could RO lock, when requesting an unlock, bounce

> <py1hon> i was actually about to bring that up

> <py1hon> that is what you'd like to be able to do

> <py1hon> however

> <py1hon> if you tell the VM developers that this is what you want to do

> <py1hon> the guys who work on the page cache code and all that crap

> Qantourisc says fucks sake, another but ?

> <py1hon> i'm pretty sure they just run away screaming

> <Qantourisc> py1hon: why ?

> <py1hon> apparently (and this part of the code I know fuck all about) swapping out the page that's mapped into userspace like this would be a giant pain in the ass

> <Qantourisc> because it's not easy ?

> <py1hon> yeah

> <py1hon> like i said, i don't know that code

> <py1hon> i would actually imagine with all the stuff that's been going on for page migration it ought to be doable these days

> <py1hon> but

> <py1hon> i am not a VM developer

> <Qantourisc> py1hon: btw howmuch room do you need to bounce ?

> <Qantourisc> as in MB's

> <py1hon> it's not the amount of memory you need, you only need it for the writes that are in flight

> <py1hon> it's the overhead of all the memcpys and the additional cache pressure that sucks

> <Qantourisc> yea

> <Qantourisc> that or you disable checksums :D

> <py1hon> yep

> <Qantourisc> maybe this should be a ionctl option one day ?

> <Qantourisc> prefebly yesterday :D

> <py1hon> eventually

> <py1hon> my priority is getting all the bugs fixed

> <Qantourisc> so if the program doesn't care about checksum, and want's is 200x speed back at 0 bounce cost

> <Qantourisc> he can have it

> <Qantourisc> py1hon: this would be a general kernel feature :)

> <Qantourisc> wich ... right you would need to add :p

> <py1hon> and realistically it's not THAT big of a performance impact

> <Qantourisc> py1hon: btw i'm still kinda set on writing code to stresstest the lot :p

> <Qantourisc> I really don't trust IO stacks

> <Qantourisc> many disks in the past have lied through their teeth

> <Qantourisc> and so has the kernel

> <py1hon> xfstests actually does have quite a few good tests for torture testing fsync

> <Qantourisc> sweet

> <Qantourisc> but i'm talking while yanking power :D

> <py1hon> and nothing fundamental has changed w.r.t. fsync since early days of bcache

> <py1hon> so that stuff has all been tested for a looong time

> <py1hon> and bcache ain't perfect if you really hammer on it, but i know about those bugs and they're fixed in bcachefs :p

> <Qantourisc> And it's just not about bcache kernel code

> <Qantourisc> it's also about disks

> <py1hon> yeah i don't want to know about whatever you find there :P

```
