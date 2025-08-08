+++
title = "Compression"
slug = "Compression"
url = "/Features/Compression/"
+++

Unlike other filesystems that typically do compression at the block level, bcachefs does compression at the extent level - variable size chunks, up to (by default) 128k.

When reading from extents that are compressed (or checksummed, or encrypted) we always have to read the entire extent - but in return we get a better compression ratio, smaller metadata, and better performance under typical workloads.

## Available options

The three currently supported algorithms are gzip, lz4, and zstd. Compression may be enabled for the entire filesystem (e.g. at format time, or via the options directory in sysfs), or on a specific file or directory via the `bcachefs setattr` command.

### Compression level

The compression level may also be optionally specified, as an integer between 0 and 15, e.g. `lz4:15`. 0 specifies the default compression level, 1 specifies the fastest and lowest compression ratio, and 15 the slowest and best compression ratio.

### Background compression

If the `background_compression` option is used, data will be compressed (or recompressed, with different options) in the background by the rebalance thread. Like the `compression` option, `background_compression` may be set for both the whole filesystem and on individual files or directories.

This lets more aggressive compression be used (e.g. `zstd:15`) without bottlenecking foreground writes.
