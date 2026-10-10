# Repeat-boot file-data and allocation trace

The fresh second-boot diagnostic reproduced corruption with unchanged storage
drivers and no XID installed. Host tracing shows requests reaching the actual
file-data addresses, yet all seven sectors covering the three new files retain
their exact preboot bytes. FAT and directory sectors changed. The unresolved
boundary is now submitted buffer contents and completion, rather than simply
whether requests reached the file-data addresses.

## Observed result

| File | First cluster | Bytes | IDE/block/root request triplets | Cold data |
| --- | ---: | ---: | ---: | --- |
| status2.log | 2681 | 274 | 6 | Exact stale parent bytes |
| payload2.txt | 2688 | 2226 | 133 | Exact stale parent bytes |
| exit2.txt | 2144562 | 4 | 1 | Exact stale parent bytes |

Each triplet is an adjacent IDE DMA WRITE, top-level block write, and matching
root-image write entry with identical byte offset and length. These are three
observations of the same request, not three independent writes. The payload
requests cover its five sectors, starting at LBA 16005872. Sector comparison
found zero changed bytes in those five sectors and in the status/exit sectors.
Five corresponding metadata sectors changed by 4, 4, 80, 97 and 65 bytes.
See emu001/trace-analysis.json, target-trace.txt and sector-comparison.json.

The full allocation scan found 12 orphan clusters, invalid terminal links for
$WinMgmt.CFG and CIM.REC, and a CIM.REC chain with 65,536 bytes capacity against
705,882 bytes advertised. All three logical files equal their corresponding
preboot free-cluster bytes. Independent qemu-nbd and qemu-img readers agree on
logical file contents, directory entries, complete FAT and selected sectors.

The phase 2 workload was launched once at 22:26:22.525 UTC on October 10, 2026.
There was no dashboard return or new EventLog 6006. The watchdog stopped the
owned guest at the end of 301.55 seconds of observation. This is a failed,
host-stopped diagnostic; scoped restart, normal restart and cold integrity are
all false. The empty new-event delta is not a boot success. Corrupt status bytes
cannot establish successful guest flush calls, readback, or an exit code.

All selected protected/staged files still match. All five registry hives remain
byte-exact and parse successfully; selected policies and device bindings are
unchanged. XID binary and SYSTEM service/image references are absent before
and after the run.

## Pinned inputs and separation of evidence

- Parent: closed no-XID first boot, SHA256
  `6de11f0ce947138eddbabfa503836f3bb4b7eb51905795238a489f1236584f97`.
  That first boot passed scoped normal restart and exact payload/allocation
  checks; its strict event result remained false for Ftdisk 49/PerfDisk 1000.
- FATX: `ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9`,
  recorded 0101 source tree `8e12297ca0ed53383fe9aaebef152c26aee5a43b`.
- ATA: `faf9639ac8d14e9c72a4a2d7b8d3a6ceb9965f8bbc79c77d89a45733d745c675`.
- Probe: unchanged no-XID build 002 control.exe, SHA256
  `337afcbe37d329384c4abc4614840b08ffda5ac8690609319f95bb968df576bc`,
  invoked as verify.exe /second. No installer or wizard-helper actions.
- Emulator: `685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890`,
  unchanged 64 MiB/controller configuration; only host trace events added.

storage-pins.json records actual prelaunch FATX/ATA/kernel/HAL/loader hashes.
Prelaunch allocation was clean. Parent hives matched its closed first-boot
capture. The first-boot result does not qualify this second boot.

The original failed XID and no-XID disks are retained. All four previously
pinned earlier images still match their hashes; the prior no-XID failure is also
hashed in preserved-images.json. The parent was verified unchanged again after
this run. No evidence disk was repaired or relaunched.

## What the trace establishes and leaves unresolved

The trace contains 36,798 complete, parsed records (3,033,133 bytes), with SHA256
`4b53c7e07bab98ba7e67fcda93d1ce4aafa16c6160e9bd5a994f95a6c3fb9cd0`.
Trace definitions and their call sites match the pinned emulator build source.
They record request entry/submission, not success, completion or buffer data.
Tracing changes timing and has no per-event timestamps; records cover the whole
emulator lifetime, including its dashboard. Nested QCOW metadata offsets were
excluded from virtual-disk address interpretation.

The observations rule out the narrow explanation that no write request reached
these file-data addresses. They do not identify FATX, ATA, DMA, or the emulator
backend as the cause, prove a guest flush completed, or establish ordinary
shutdown durability. Capture the source bytes, MDL/PFN mapping, DMA scatter/gather
bytes and completion status in a fresh bounded diagnostic before any driver
change. NEXT.md describes that comparison.

All owned processes and build/xemu/UI leases are closed. No physical-console,
shared baseline, candidate integration, GPU or native ownership changes.
