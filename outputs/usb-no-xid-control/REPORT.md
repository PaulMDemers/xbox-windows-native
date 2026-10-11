# No-XID two-boot storage control

The second boot reproduced stale file data and broken allocation chains without
XID installed. XID is therefore not necessary for this observed class of
repeat-boot failure. The responsible storage component remains unresolved.

| Trial | First boot | Second boot |
| --- | --- | --- |
| Earlier XID restart trial | Scoped normal restart and cold integrity passed | Stale log/exit data, broken WMI chain, 1 orphan cluster |
| This storage-only control | Scoped normal restart and cold integrity passed | Stale status/payload/exit data, broken WMI chains, 12 orphan clusters |

Both failed second boots were stopped by the host watchdog. Neither qualifies
normal-shutdown durability. The failed control's status bytes are corrupt, so
its file lengths cannot establish successful flush calls, guest readback,
restart progression, or an exit code.

## Design and limits

The control keeps the immutable USB seed, Windows providers/core drivers,
pinned xemu binary, 64 MiB setting, controller configuration, and bounded
launch/observation procedure used by the earlier trial. Both boots exclude the
XID driver binary and installation. Full SYSTEM traversal found no xwnxid
service or string references before or after either boot.

The storage-only probe substitutes a deterministic, phase-specific 2,226-byte
ASCII payload written using 75 synchronous WriteFile/FlushFileBuffers pairs,
then closed, reopened, and compared. Its authored file names, allocation layout,
and timing differ from the HID workload. The first boot also handles the exact
known unbound controller wizard. This is a baseline and boot-sequence control,
not an exact HID replay; see comparison-design.json. It does not establish that
the two failures share an identical underlying cause.

## First boot: scoped pass

emu001 completed guest payload readback, canceled four known emulator wizards,
joined the helper with exit zero, observed 5,100 ms of stable setup idle, and
requested a normal, unforced restart. Dashboard return and one new EventLog 6006
confirmed the restart. Cold payload bytes matched exactly; protected/staged
files matched; all five hives parsed; full allocation had no errors or orphans.

Ftdisk 49 and PerfDisk 1000 remain in this boot's event delta. Therefore the strict
whole-boot event result is false, despite the scoped restart/integrity pass.

## Second boot: failure

emu002 used a fresh child of the closed first-boot disk. Its parent payloads,
hives and allocation were checked before launch. It performed no installation
or wizard-helper actions. Windows launch was accepted at 21:09:09 UTC on
2026-10-10. The watchdog ended observation after about five minutes without
dashboard return or a new shutdown event.

Two independent cold readers agree on the whole FAT, directory entries, and
logical file contents. All three new files contain exactly the bytes that
occupied their previously free clusters before the boot:

| File | Bytes | First cluster | Result |
| --- | ---: | ---: | --- |
| status2.log | 274 | 2680 | Entire file equals preboot stale bytes |
| payload2.txt | 2226 | 2687 | Entire file equals preboot stale bytes |
| exit2.txt | 4 | 2144562 | Entire file equals preboot stale bytes |

The expected payload SHA256 is
`b75a944b0372b5c98bdeda88cdbe594de66f63e897522d58ccb813ac05c5cdf9`;
the actual SHA256 is
`a622bf399b7ca332f88181562976614c38262bd4c61c3f5af8ac08fd3d8e2671`.

The allocation audit found 12 orphan clusters and invalid terminal links for
$WinMgmt.CFG (cluster 2144547) and CIM.REC (cluster 2144531). CIM.REC still advertises
705,882 bytes but its reachable chain holds only 65,536 bytes. Its starting
FAT link changed from 2144532 to 0. Full details are in emu002/forensics.json and
emu002/after/allocation.json.

All five registry hives remained byte-exact and parsed successfully. Selected
policy remained unchanged and no device-binding deltas appeared. The empty
new-event delta does not establish successful execution or shutdown.

## Build and evidence preservation

Build002 passed strict compiler warnings and actual NT5 provider import/export
checks. The exact-instance wizard policy passed 390 checks. Build001's failed
misleading-indentation warning is retained; no guest ran that build. No driver
binary was built or changed for this experiment.

- control.exe SHA256: `337afcbe37d329384c4abc4614840b08ffda5ac8690609319f95bb968df576bc`
- wizard.exe SHA256: `33558f1cec9778727b7c76642f6c647217cdf3c6f661f53b06dcb2f344f19eb9`
- Closed first-boot parent SHA256: `6de11f0ce947138eddbabfa503836f3bb4b7eb51905795238a489f1236584f97`

The parent and all three earlier disk artifacts were rehashed and are unchanged.
Raw disk/hive/binary evidence remains in private E: storage; source, hashes,
audits and comparison records are retained here. Prelaunch records pin each
boot's exact source snapshot. All owned guests and resource leases are closed.
Do not relaunch or repair these evidence disks.

## Next step

Use a fresh diagnostic child to trace baseline file-data writes alongside FAT
and directory updates, then identify where persistence diverges. Resolve this
storage failure before changing XID lifecycle behavior or attempting hardware
qualification. No physical console, shared baseline, GPU/native candidate, or
integration changes were made.
