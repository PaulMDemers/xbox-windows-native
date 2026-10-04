# Read-only physical storage metadata probe

Uploaded and readback-verified at `F:\Applications\XWNMetadata\default.xbe`.
Physical execution is pending. It reads three sectors via read-only Xbox-kernel
device handles: sector 0, sector 3, and the queried F: start. Only its own
`xwn-storage-metadata.txt` report is written. It flushes the log and reboots after
15 seconds. No physical remote launch was performed.

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
