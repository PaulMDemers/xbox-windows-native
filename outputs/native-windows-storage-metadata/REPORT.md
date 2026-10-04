# Read-only physical storage metadata probe

Uploaded and readback-verified at `F:\Applications\XWNMetadata\default.xbe`.
Physical execution passed in `physical-cycle-001`. It reads three sectors via read-only Xbox-kernel
device handles: sector 0, sector 3, and the queried F: start. Only its own
`xwn-storage-metadata.txt` report is written. It flushes the log and reboots after
15 seconds. The user subsequently authorized the FTP launch recorded below.

Owned emulator run `storage-metadata-001` completed the reads and rebooted to
UnleashX. It found the synthetic PARTINFO, BRFR and FATX data. The table parser
correctly rejected the 250 GB extent against the older BIOS's reported
137,438,952,960-byte disk capacity. `METADATA_COMPLETE success=1` denotes
completed reads, not partition-table acceptance. Physical capacity is not
inferred from this emulator result.

The executable hash is recorded in `validation.json` and `ftp-upload.json`.
After testing, only the introductory source comment was corrected to describe
the three sector reads accurately; no executable code changed or new upload
occurred. The report/evidence are retained. The disposable run disk and original
synthetic fixture were reclaimed after host space exhaustion; they are
reproducible using `prepare-fixture.py`. A compressed derivative is retained at
`work/extended-read-fixture.qcow2` and described by the extended-partitions kit.

## Physical automated cycle — 16:00 UTC

The exact uploaded XBE was verified over FTP before sending
`SITE EXEC F:\Applications\XWNMetadata\default.xbe`. UnleashX returned 200.
No report existed before launch. A fresh, complete report was retrieved about
67 seconds later, following the probe's automatic reboot. No user console
input was requested during this cycle. FTP was available again afterward.

The physical report accepts PARTINFO with six active partitions. E: ends
exactly where F: starts; F: ends exactly at the queried disk capacity. The raw
C: table entry is within the disk, unlike the earlier virtual C: query. BRFR
and the F: FATX superblock are present; F: uses 128 sectors per cluster (64 KiB).
The six extents exactly match the synthetic emulator fixture. These reads
used the existing Xbox kernel; native Windows F: I/O remains untested.

`remote-cycle.py` records launch and retrieval separately, verifies the XBE,
and prevents a stale report from being mistaken for fresh output. If a prior
report exists it is saved locally and renamed remotely before launch. An
uncertain launch must not be repeated automatically. This loop applies to
bounded probes which reboot successfully; a hung Windows handoff may still
require a physical reset.
