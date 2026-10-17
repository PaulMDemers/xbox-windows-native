# Read-only ownership before image mapping

The reader accepts an absolute bounded byte-read callback for an immutable/offline
volume, parses FAT16/FAT32 entries and recursively claims directory/file chains.
It rejects crosslinks, cycles, missing/free/bad/reserved links, unexplained allocated
clusters, malformed entries, duplicate ASCII-folded names and capacity overflow.
Only after a complete scan and header/FAT reread may a contiguous ASCII short path
resolve. A failed scan cannot be reused. Non-ASCII names still claim allocation;
their OEM case-fold semantics are not implemented and are not native namespace
qualification. Repeated identical metadata reads are not concurrent-write or ABA
exclusion. Parent FATX must be offline for this prototype.

Limits are1,048,576 clusters,32,768 entries,2,048 directories,depth32 and4 MiB per
read. Native nonpaged allocation budgets and bounded boot work remain unproved.
The separate NTFS header checker accepts only512-byte sectors, matching primary
and backup, bounded MFT/mirror positions, supported record sizes, exact hidden
offset/serial/extent. It is not a complete NTFS/MFT consistency checker.

The fixture's independent FATX writer creates a small raw volume with a marker
outside it. Real NTFS tools format/insert/extract the long-name file. Projection
reads all32 MiB in bounded chunks, compares them byte-for-byte with the original,
and repeats extraction with a separate filesystem tool. No existing disk is
modified. The high-LBA test uses synthetic translated reads only.
