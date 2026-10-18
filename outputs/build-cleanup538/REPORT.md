# Authorized obsolete-fixture cleanup538

The user explicitly authorized removing old builds to free space and resume.
Removed exactly six generated negative-test QCOW2 copies for bootvideo,
mmcomplete and processinit (bad-hal / bad-kernel). These were full converted
copies, not source media, release/recovery packages, good fixtures, runtime
logs or active test inputs. All historical outcomes and failure records remain.
Reconstruction scripts, packages and original fixture hashes remain. Each deleted
private path has a small `.removed538.json` pointer. Reconstruct only as a new
attempt if needed; do not rerun closed historical runtimes.

Allocated bytes removed: 6,200,557,568. Measured C: free-space gain:
6,200,553,472 bytes (about 5.77 GiB); free space after: 27,628,158,976 bytes.
No host E: deletion, file moves, backing-volume operation, firmware/console
access or source/driver change occurred during cleanup.

Safety evidence: inventory001 records SHA256/size/single-link metadata,
resolved exact local paths, original fixture records, closed-run cleanup records,
all 52 active536 package pins and 1,543 host QCOW headers. No active dependent
image was found. wsl-check001 separately checked 23 WSL fixture/PC images.
The broad WSL find was terminated after over two minutes; its empty partial
output was NOT a complete inventory. The supplemental scan excludes source,
build and toolchain trees. Historical fixture consumers use full Copy-Item,
not dependent QCOW overlays. No emulator process was active.

Deletion used PowerShell Remove-Item -LiteralPath on six exact files only,
without recursion, after checking allowlist, directory boundaries, reparse
parents, sizes and every hash before any deletion. cleanup001 is the receipt.
Recovery/private256 and the current536 parent binaries and snapshots remain.

Next: collect the already-run536 warm case through a NEW after1-only supervisor
identity. The earlier capacity-refused supervisor remains unchanged; it created
no capture and issued no FTP operation. Do not launch another warm test.
