# 426: fixed NTFS image on FATX, selected for a prototype

This is a design choice and a host model, not installed filesystem support.
No loader, driver, registry, dashboard or physical console is changed. The
six lossless-transfer exclusions and all existing strict gates remain failures.

## Evidence and choice

425 observes native requests for 44-byte SID directories and 69-byte RSA files
returning STATUS_NAME_TOO_LONG. 423's ordinary PC NTFS control retains these
names and the cryptographic operations work across restart. These are good
reasons to retain NTFS semantics, not evidence that NTFS already boots through
a FATX image on Xbox. COM+ still needs a functional test.

| Requirement | Logical names over FATX | Fixed file containing NTFS |
|---|---|---|
| Names, case, enumeration, directory rename | New namespace metadata and lookup rules in every path | Delegate inner namespace to NTFS after genuine block-device integration |
| Existing Xbox boot | Keep physical FATX boot files, but loader must understand any aliased boot paths | New ARC image device and early Windows disk/volume handoff required |
| Dashboard | Sees aliases and metadata it cannot interpret; arbitrary external changes ambiguous | Sees one ordinary short-named image; cannot browse inner files directly |
| Old FATX drivers | Cannot force unmodified old drivers to honor a new metadata marker | See an ordinary file; deletion/resize remains dangerous, no automatic protection claim |
| Crash recovery | New transaction ordering across FAT, directory and namespace metadata | Fixed outer allocation; inner NTFS recovery plus real lower flush semantics required |
| Stock disk capacity | No full image preallocation | Image must fit E alongside Apps, launcher and recovery margin |
| Size | Existing per-file format bound | One FATX file has a 32-bit length; first prototype must stay below 4 GiB |

Select the **fixed image route for the next bounded prototype**, because it
avoids inventing Windows name and security-state storage semantics. This is
conditional on proving an early boot/storage handoff without recursion or
allocation races. If that cannot be established, revisit the decision rather
than widening the current FATX name field or introducing unreviewed aliases.

## Reviewed source boundaries

Public overlay source is a partial upstream overlay, not the complete tree.
`source-review001.json` pins the reviewed files and the upstream enumeration
source from the actual403 materialized tree. No upstream source is relicensed.

- `vfat.h`: FATX names are a counted 42-byte array and file size is ULONG.
- `dirwr.c`: FATXAddEntry rejects names above42; rename converts into43-byte
  scratch and rejects an encoded length above42. Delete marks the physical
  slot and frees the FAT chain; moving saves cluster/size metadata.
- `fcb.c`: vfatDirFindFile compares the enumerated Unicode long/short names
  case-insensitively. `direntry.c` derives both names from the single OEM field.
- `finfo.c`: rename can replace an existing target, moves directory entries
  and updates descendant FCB paths; EOF changes allocation. A create-only
  alias trick would miss these paths and open-handle semantics.
- FreeLoader `fs.c` registers filesystem mount functions including NTFS;
  `ntfs.c` reads through ArcSeek/ArcRead on an underlying DeviceId. This is a
  useful reader boundary, not an existing file-to-block implementation.
- `disk/part_brfr.c` maps Xbox partitions, including standard dashboard E and C.
  Replacing E's FATX format with NTFS would break the dashboard use of E.
- `include/xwnvolume.h` contains an earlier read-only installed-NTFS file
  checker which explicitly stops before Windows. It does not qualify boot.
- Current install/recovery documents and install-stock-e tooling operate on
  ordinary files or whole E. None qualifies image-backed Windows recovery.

## Proposed storage and boot contract (unimplemented)

1. Keep dashboard C untouched. Keep launcher, descriptor and fixed image under
   short FATX names on E. First size target is 2 GiB, subject to measured payload,
   free-space and NTFS growth/pagefile needs; this is not yet a capacity result.
   No sparse image, grow-on-write, compression, online resize or multi-file
   splitting. FATX maximum sector-aligned file length is 0xfffffe00; initial
   implementation may use a stricter cap. Do not load the image into64 MiB RAM.
2. Provision a new unused file, finish its data/metadata writes, flush, then
   independently read back payload and the complete FATX allocation. Detect
   loops, short/extra chains, crosslinks and directory/metadata overlap. Publish
   a versioned descriptor only after those checks. Keep the existing launcher
   active until the new image and descriptor have both passed cold validation.
   A torn descriptor is a refusal, never permission to guess physical offsets.
3. At each boot derive the chain from actual FATX metadata, compare the current
   identity/length/geometry and descriptor, and establish exclusive ownership
   before publishing the immutable map. Any external move, resize, replacement
   or inconsistent chain requires revalidation; never replay stale extents.
   Hashes detect accidental corruption, not malicious tampering or rollback.
   Identical-size/serial replacement is not excluded by this model. A complete
   offline content/identity policy must be specified before implementation.
4. Loader exposes bounded image-relative reads through a new ARC device. Boot
   registry, NTFS driver and image block driver must be discoverable without
   first mounting the inner filesystem in Windows. Kernel receives a pinned,
   versioned handoff but independently validates it against the actual disk.
   The device/partition/ARC naming and boot service initialization order remain
   unresolved; prove them from exact NT5 loader/kernel paths before coding.
5. Kernel routes inner sectors directly through the verified map to the owned
   lower storage device. Do not recursively open the backing file through the
   same filesystem during paging. Keep all dispatch metadata nonpaged and bound
   memory use; model cluster-count cap is not a kernel allocation guarantee.
6. Parent E must remain exclusively reserved against filesystem writes and
   cached aliases while mapped. Holding a generic FileObject or marking a file
   read-only is insufficient. The safest initial design keeps parent E
   unmounted in Windows, but the concrete device enforcement is still open.
   Other partitions remain separately bounded. Boot-time scans alone cannot
   protect against later reallocation. Do not hide this as a successful lease.
7. Translate the entire request before IO. Reject unaligned/overflowing/outside
   EOF requests, then split at cluster boundaries. Preserve 64-bit absolute
   offsets even when image length is below4 GiB. No request may touch FATX
   metadata, image slack, unrelated E files or dashboard C. The model's geometry
   supplies an allowed partition; it does not discover the real E partition.
8. A short/failed lower write is a failed request, possibly with partial media
   changes. Propagate errors, retain the map and quarantine further IO. Never
   report success or attempt a fabricated rollback. Implement proper IRP
   cancellation/concurrency/lifetime semantics before an actual driver.
9. Successful flush must reach and be acknowledged by actual lower hardware.
   A model callback returning true is not proof of hardware durability. Drain
   in-flight operations before dismount/unpin; real barriers and shutdown order
   need tests. NTFS recovery is required after interruption; this model neither
   implements nor proves journal or file-content recovery.
10. Paging and crash-dump paths need their own mapped-storage support, including
    high-LBA behavior, allocation residency and dump-stack initialization. Do
    not disable dumps or waive current Ftdisk49 to make the image boot pass.

## Dashboard, install and restore behavior

The dashboard can copy or back up the CLOSED image but cannot browse Windows
files inside it. Normal Windows rename/case/long-name behavior happens within
NTFS, with no FATX aliases exposed. A future host extraction/import utility must
preserve the original NTFS names and metadata; FTPing an unpacked tree to FATX
still loses representability and remains rejected by tools/fatx_names.py.

An old driver/dashboard can still delete or alter the backing file. The plan
does not claim otherwise. Dedicated installation instructions must prohibit
in-place edits, require Windows shutdown and readback after transfer, and avoid
automatic fallback to an unrelated image. Offline restore should use a new
file, fresh allocation audit/descriptor, and launcher-last activation. The old
bootable installation and recovery route stay intact until qualified. Existing
whole-E recovery remains a separate tested operation, not proof of image restore.

## What model.py actually implements

Original MIT Python only: bounded immutable extent construction from supplied
geometry/chain/complete owner tuples; sector translation; a canonical descriptor
compared with a supplied fresh map; sequential IO/flush/quarantine lifecycle.
There is no NTFS implementation, on-disk FAT parser, actual allocator, boot
device, registry patch, exclusive lease, async IRP, filesystem journal or hardware
flush. Owners, IDs and lower completion are explicit host inputs/models.

All shorter descriptor prefixes, bit mutations and extra transport bytes refuse.
This models partial descriptor publication only, not every possible torn sector
or content corruption. No double-slot atomicity is claimed. A fully old valid
descriptor is not an anti-rollback failure; no monotonic counter is implemented.
No live allocation updates occur, so transaction IDs, name collision rules and
rename journaling belong to NTFS rather than a new FATX naming model.
