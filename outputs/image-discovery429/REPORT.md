# Real FATX image discovery and NTFS byte projection

The new read-only host reader found a contiguous WINDOWS.IMG in a fresh miniature
FATX volume and projected every byte of its real 32 MiB NTFS payload exactly.
The independent ntfscat recovered an 8,193-byte payload under a 69-character name
from both the original and projected NTFS files. The raw disk and outside-volume
marker remained unchanged. This advances the long-name storage route beyond the
427 modeled map. It is not a native loader, Windows mount or bootable solution.

fixture001 uses owned pinned mkntfs/ntfscp/ntfscat binaries, an independent FATX
writer, and the new full-ownership reader. It scans one directory, one file and
8,209 owned clusters. The wrapper file has 8,208 clusters, begins at byte1089536,
and the NTFS payload begins at byte1155072 after its 64 KiB wrapper. The 65 MiB
raw fixture, original/projected NTFS and payload hashes are in fixture001.json.
All are private under E:/xwn429/fixture001; no proprietary OS image was created.

tests001 passes 50 actual-fixture mutations and synthetic cases: invalid chains,
crosslinks, orphans, short reads, quarantined scans, metadata changes, capacities,
fragmentation, FAT32 and a synthetic origin above128 GiB, plus NTFS header and
backup-semantic failures. High-origin arithmetic is not physical large-LBA IO.
The original fixture is hash-unchanged. All commands are closed; no native build,
guest launch, physical access, driver/SDK change or actual install occurred.

The inner NTFS header's total-sector field is65535 for a65536-sector file; its
last sector holds the backup. This matches the actual formatter output and the
backup-reservation behavior in [mkntfs source](https://github.com/tuxera/ntfs-3g/blob/edge/ntfsprogs/mkntfs.c).
That linked branch is explanatory, not an immutable source pin. The exact used
formatter executables are pinned; a full dynamic-library/source closure remains
needed before native/release reconstruction.
