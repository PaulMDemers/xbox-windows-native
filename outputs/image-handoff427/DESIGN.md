# 427: contiguous image projection through the existing partition path

Refine426's fixed NTFS image proposal: the first candidate should require a
**single contiguous FATX allocation**. FreeLoader and the Xbox HAL would both
project the inner NTFS range as partition1, replacing the enclosing dashboard E
range in Windows' partition enumeration. The existing NT5 disk/partition stack
would then handle requests at the real offset. No new file-backed virtual disk
driver is proposed for this initial path. Fragmented files are a hard refusal.

This is an uninstalled design and host prototype. No native source changed.
426's fragmented translator remains valid host evidence but is not the selected
native implementation. A generic fragmented image driver would still need the
early disk-device, IRP, nonpaged extent and dump integration discussed there.

## Reviewed boot path

1. FreeLoader `DiskInitialize` computes the actual sector-zero checksum. For a
   BRFR Xbox disk without a valid MBR it supplies synthetic signature0xaa55 and
   marks the partition table valid. Keep that disk identity unchanged; the new
   image range is not a second physical disk and must not invent an MBR.
2. `DiskGetBrfrPartitionEntry` currently returns E as partition1. A future opt-in
   adapter must independently resolve and validate the FATX image before any
   `partition(1)` NTFS read, then return the inner range/type instead of E.
   Parent lookup must use bounded raw disk reads, not recursively open the
   projected partition. Launcher configuration still resides outside the image.
3. `WinLdrInitSystemHive`/`WinLdrLoadSystemHive` read SYSTEM through ARC and derive
   `BootFileSystem` with `FsGetServiceName`. The existing NTFS table reports
   `ntfs`. `WinLdrScanRegistry` uses CmpFindDrivers, group/tag sorting and dependency
   resolution, then WinLdrLoadBootDrivers preloads those binaries from BootPath.
4. `WinLdrInitializePhase1` fills ArcBootDeviceName, NtBootPathName and the ARC disk
   signature list. Retain the physical disk/partition ordinal while using the
   projected range for reads. ArcHalDeviceName must name a runtime-valid system
   partition too; the loader's launch location cannot be assumed to remain
   mounted as outer E in Windows. Explicitly test both names and SystemRoot.
5. Current HAL `HalInitSystem(0)` calls `HalpInitPhase0`, whose Xbox implementation
   installs `HalpXboxInitPartIo`. It replaces the partition-table dispatch before
   later disk enumeration. This is a real existing source path, not a proposal
   for a late driver callback. Historical physical hook-registration evidence
   is separate: it halted before partition handling and proves no new mapping.
6. `HalpXboxIoReadPartitionTable` already reads Xbox metadata via its lower disk
   device and returns a synthesized DRIVE_LAYOUT_INFORMATION. A future image
   branch validates the current disk/file/header independently, then substitutes
   only partition1 with the NTFS range. Existing set/write-layout handlers reject
   changes to Xbox layouts. Preserve that protection and the untouched entries.
7. Static review of the owned NT5 kernel identifies calls from
   IopInitializeBootDrivers to IopWaitForBootDevicesStarted (RVA14b2cf/14b334),
   then IopCreateArcNames (14b340) on the inspected successful path. IoInitSystem
   calls boot-driver initialization at149d69, SystemRoot reassignment at149e20
   and the HAL drive-letter wrapper at149e7e. These are pinned static callsites,
   not new runtime ordering observations or complete control-flow proof.
8. Fresh private registry provisioning must map Windows C to signature0xaa55
   plus the **inner** partition start. Existing405 provision code maps it to
   outer E's5633024*512; copying that value unchanged is wrong. Update only the
   intended fresh image's matching mount identities and independently compare
   raw registry values. Never change the current demo registry for this work.

The Microsoft kernel source is not being substituted with ReactOS source.
Kernel observations above come from the exact owned executable and its validated
symbols. Reviewed loader/HAL files come from recorded403 materialized trees;
source-review001 records whether the current overlay matches each full source.

## Allocation and identity contract

Proposed single file: short FATX path, a64 KiB immutable wrapper prefix followed
by the NTFS partition. `projection.py` defines an experimental512-byte envelope
within that prefix: version, exact length, zero flags/reserved padding,16-byte
image identity, disk/parent/file/inner geometry, NTFS serial and SHA-256 checksum.
No real file currently uses this format. Header format must be reviewed again
against the native parser before freezing it as an installer interface.

The prefix remains outside the projected NTFS volume, so normal NTFS writes
cannot alter the identity header. Expected image identity comes from the selected
launch entry, not from accepting whatever header happens to be present. Loader
and HAL each validate the header, complete FATX chain, exact EOF, contiguous
allocation, parent geometry and inner NTFS identity; never trust saved absolute
offsets alone. An allocation move refuses until an offline verified reprovision.

The whole allocated cluster chain, including prefix and EOF slack, must be
crosslink-free and disjoint from directories/metadata/other files. A future full
ownership scan is mandatory; the model receives those facts from426's supplied
owner map. A first-cluster check or merely counting successive FAT links is not
enough to exclude a second file referencing the same clusters.

The checksum/UUID are accidental mismatch defenses, not authentication against
an attacker who can rewrite both launch config and file. Deliberate cloned IDs
and forged geometry require stronger authenticated provisioning if that threat
is in scope. Cold payload hashes are installation/restore verification, not an
immutable hash of a Windows volume that changes legitimately during use.

Only partition1's range/type changes in the host projection. No enclosing E
device is returned, and no overlapping partition is added. All other partition
records, especially dashboard C, remain identical. This prevents ordinary
filesystem mounting of outer E **if the native implementation enumerates exactly
this layout from the start**; it is not protection against privileged raw disk
writes through Partition0 or an unreviewed alternative enumeration path. There
is no real exclusion proof yet. All discovery paths must be inventoried in the
read-only native experiment. Do not claim a lease from the header alone.

## Bounds, lifecycle and recovery

- Initial install target remains2 GiB of NTFS plus64 KiB wrapper, subject to
  measured stock-E free space and pagefile/growth needs. Maximum wrapper+payload
  must fit a FATX32-bit file size. Sector size is512; all offsets use checked64-bit
  arithmetic. The initial hidden-sector LBA must fit32 bits; >128 GiB offsets
  are included, but arbitrary >2 TiB placement is not claimed.
- Proposed raw scanner budget:64 KiB read scratch, bounded directory traversal
  depth/path, and a bitset covering all parent clusters. For a reviewed stock E
  cluster count below1,048,576, one ownership bitset is at most128 KiB. Need
  separate visited-directory/active-chain state, at most another128 KiB plus
  bounded stacks. Refuse larger counts until a budgeted algorithm is reviewed.
  These are design budgets, not measured native allocations. No full image inRAM.
- The final published projection is constant-sized. No NTFS request needs the
  outer FAT map during ordinary IO, paging or high-IRQL dump writes; the existing
  disk stack uses a real physical partition offset. This reduces new machinery,
  but actual pagefile/dump initialization, high-LBA commands and recovery still
  require tests. Do not suppress Ftdisk49 or disable dumps.
- No online image growth, move, rename, container write or FATX metadata update.
  Dashboard runs only after Windows stops. During Windows, ordinary outer-E
  access is unavailable; applications live inside NTFS. Backup the CLOSED file.
- A mismatch during HAL validation must return failure and leave the image
  unexposed. Never fall back to the old E range with the same boot ARC identity.
  A later repeated partition query must reproduce the pinned projection or fail,
  not silently switch live partition geometry. Native one-time publication and
  concurrent-query lifetime are not implemented in this host prototype.
- Power loss during NTFS writes invokes NTFS recovery on next boot; outer FATX
  allocation should remain unchanged because no outer writer ran. This remains
  a test requirement, not proof of transactional/durable payload writes.
- Interrupted installation must leave old launcher active. Restore to a new
  closed file, validate full FATX allocation/header/payload, then activate a
  matching entry last. Preserve original demo and rollback before any trial.

## Next native discriminator

Implement a reusable, bounded raw FATX resolver/full-owner validator and compare
its findings independently on a newly prepared disposable image, initially
read-only. Then use a loader-only opt-in projection that reads selected NTFS files
and halts before kernel entry. The loader needs no new ARC device if the existing
partition path is correctly overridden. Preserve ordinary entry behavior exactly.

Only after that read-only result should a separate HAL opt-in branch return the
same independently validated projection. Trace actual partition enumeration,
ARC links, SystemRoot, mounted-device identities and absence of outer E before
allowing a writable NTFS boot. That proof cannot be replaced by host booleans or
the old physical registration result. Full crypto/COM+/namespace/install/restore
and cold audits still gate the clean-install release.

## Symbol validation correction

static001 refused before disassembly because it incorrectly required PDB stream1
age equal to the image age. Actual values are image1, PDB2, DBI1, same signature.
Microsoft's `PDB1::OpenValidate4` checks that PDB age is at least image age and
that a nonzero DBI age equals image age. static002 adds the DBI header validation
and requires the exact nonzero DBI age; original001 remains a failed attempt.
See [Microsoft validation implementation](https://github.com/microsoft/microsoft-pdb/blob/master/PDB/dbi/pdb.cpp#L745-L821)
and [DBI header layout](https://github.com/microsoft/microsoft-pdb/blob/master/PDB/dbi/dbi.h#L116-L129).
No PDB or executable was edited; private disassembly stays onE.
