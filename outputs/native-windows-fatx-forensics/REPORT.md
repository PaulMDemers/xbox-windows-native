# Physical cycle013: preserved allocation corruption

The physical 300-case test finished its mapped/truncate and 32 MiB asynchronous
write phases, then crashed during its five-minute background pause. The user
reported `0xA (0x10, 0x2, 0x0, 0x82423167)`. The kernel load base for this boot
has not been established, so no function attribution is claimed. Test payloads
still match their expected patterns after reboot. This is a failed stability
trial, despite cycle012's earlier bounded pass and complete binary audit.

FTP readback of `winnt/system32/drivers/xwnfatx.sys` returns 65536 bytes then
426; its first cluster contains UTF-16 WMI MOF text instead of an executable
header. A prefix matches the owned `cimwin32.mof` at byte454256, but the whole
cluster does not match that source slice. `CIM.REP` also reads short. The old
filesystem backup, current HAL and trace miniport retain their expected hashes.

## Read-only physical snapshot

The original nxdk tool in `main.c` opens Partition6 for read access only, verifies
its pinned start/size and FATX header, and reads the FAT plus bounded chains for
the Windows driver and WMI repository. Output uses new files beside the XBE on
E:. It does not repair FAT entries, reset WMI, or boot Windows. The result marker
means capture completed; it does not mean the captured filesystem is healthy.

Before physical use, emulator `fatx-forensics-002` verified every saved metadata
and cluster byte against the stopped disk. The run's top overlay has no F: data
extents. An earlier emulator attempt stopped at the partition-size guard because
the owned Xbox BIOS exposes only its LBA28 prefix; the tool now permits that
exact emulator prefix while using the pinned full-volume FAT geometry and
enforcing the actual read-handle bounds. Physical Partition6 reports the full
242055217152 bytes. Firmware and all raw files remain local and ignored.

XBE SHA256: `e87fb1840c812da2ca1287ceef0c5eb9134e18d192816824e1bda553b4ba0890`.
One physical launch at 2026-10-05 00:44:24 UTC returned to the dashboard. The
source F: volume was only read; outputs are `E:/Applications/XWNFatRO` and local
`artifacts/physical-013`. `physical-snapshot.json` records every file hash.

Captured metadata SHA256:
`c292ba76214ba2cb3a3475741fc6506348cde56fc7ee7f022285188b8a488bc1`.

- `xwnfatx.sys`: directory size167789, first cluster2154674, FAT entry zero
  (free). The saved cluster exactly matches the corrupt FTP prefix. Its absolute
  disk offset is149227560960 bytes, beyond LBA28.
- `CIM.REP`: directory size2686976, chain37 clusters/2424832 bytes: four clusters
  (262144 bytes) short. It ends at a valid end marker, rather than a read failure.
- `$WinMgmt.CFG`: size12, first cluster2160625 is also marked free.
- `xwnfatx.xwn-c11`: its original three-cluster chain remains valid.

`analyze-snapshot.py` inspects1374 entries in six captured directory clusters.
Those three entries are inconsistent; no chain overlaps are found among the
captured entries. This is not a whole-volume audit. It does not establish which
operation first freed or reused the affected clusters, and cannot rule out
cross-links involving uncaptured directories.

## Emulator comparison and next experiment

`nt5-physical-f-cache-soak-001` used the same production filesystem, helper and
cycle012 registry snapshots. It completed300 cases, pressure, five-minute soak
and normal restart; cold payload checks and3439 immutable binaries passed.
During a parallel attempt to create a full snapshot fixture, the host ran low
on disk space. That failed generated file was removed, the VM was paused/resumed,
and the final dashboard captured. No guest I/O error was recorded, but this
interruption prevents treating the run as a pristine qualification. Subsequent
fixtures use small overlays. The physical corruption was not reproduced.

The original emulator places Windows low on F:, whereas the physical install
is above LBA28. `prepare-high-allocation.py` creates a separate experiment with
the driver and WMI repository on fragmented high clusters, and marks otherwise
free lower clusters unavailable so new allocations occur in that region. It
preserves source hashes and verifies relocated file contents. It is a synthetic
allocator/layout test, not a clone of the physical disk or a hardware fix.

### High-allocation run001 failed in WMI rename

The new fixture SHA256 is
`18a72152df86ef61608836698758b0153ac365729518a89ed39ae93863d7d95c`.
Run `nt5-physical-f-high-allocation-001` launched at00:50:26 UTC, completed300
mapped cases and pressure, and crashed during the background soak. The screen
shows `0x1E (0xC0000005, 0x824C7A22, 0x1, 0x006FFFC8)`. Registers,60MiB of
physical RAM and the stopped disk overlay are preserved locally. This is an
emulator failure with a different stop code, not proof of the same corrupting
operation as physical013. The harness is closed and no VM remains running.

Page-table/PE analysis establishes kernel base`823dd000`. Matching kernel
symbols and instruction boundaries place the original fault at
`RtlUnicodeToOemN+0x5a`, writing to`006fffc8`. Both a saved CONTEXT and trap-frame
candidate agree on these registers. Caller frames lead through
`RtlUnicodeStringToOemString` to the filesystem's `vfatRenameEntry`, RVA`7cd6`
at loaded driver base`fe43b000`; matching COFF disassembly confirms that call.
The input name is`$WinMgmt.CFG.BAK`. Post-fault locals contain directory pointer
`006fffc6`, OEM output pointer`006fffc8`, and cache context`fe66ae08`.

The rename source ignores the Boolean result of `CcPinRead` before using its
output, and converts directly into the counted directory field. The captured
state does not record that Boolean result: a failed pin and corrupted cache
mapping must be distinguished at a breakpoint before selecting a fix. A later
fault occurred while rendering the bugcheck; the halt registers are not the
original rename registers. `analyze-crash.py` retains that distinction and stops
frame interpretation at trap transitions instead of treating pool links as
call frames.

Cold inspection finds the report ends at the same soak-start marker as physical013.
The preexisting relocated driver and CIM.REP chains are still valid, unlike
physical013. The newly allocated `$WinMgmt.CFG` points to a free FAT entry;
new test files are absent from the persisted root directory. Unflushed metadata
after a crash can account for some of these differences, so these are not proof
of the same corruption. The strict cold audit fails at that CFG chain after
475 files/197 immutable binaries; no full-audit pass is claimed.

Next: repeat this exact emulator fixture with a breakpoint at the rename
`CcPinRead` return, capture its result/output pointers and BCB/VACB state, then
test a targeted repair against both low and high allocation cases. Preserve the
bad physical install while establishing whether the cache pin failed or its
mapping was already corrupt. Host C: has about1.1GiB free; use bounded deltas and
one temporary raw conversion at a time.

Keep the physical install unlaunched until the corrupting operation is understood
and restoration can be verified. Cycle014 Paint testing remains gated off.
Do not overwrite the damaged driver or reset WMI merely to obtain another boot.
