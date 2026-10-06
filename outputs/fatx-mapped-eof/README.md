# Real NT5 mapped-file EOF regression

This is an emulator-only comparison of FATX 0088 and 0098. The physical baseline,
release 0.1.0 and its recovery bundles are untouched. Candidate 0098 is the exact
fresh build recorded in [the paging EOF work](../fatx-paging-eof/README.md).
There is no new driver patch in this experiment.

## Results

Both ordinary attempts are closed. [Summary](summary.json) and the individual
[old-driver audit](old/audit.json) and [fixed-driver audit](fixed/audit.json)
retain the measured results.

| Check | FATX0088 control | FATX0098 |
|---|---:|---:|
| Real mappings checked | 153 | 153 |
| Nonzero EOF-tail failures | 74 | 0 |
| In-file byte mismatches | 0 | 0 |
| Exact cold input/output contents | 34/34 | 34/34 |
| Allocation errors / orphan clusters | 0 / 0 | 0 / 0 |
| Normal shutdowns | 1 | 1 |
| New shutdown popup | 1 | 0 |

The control exposed the deliberate 0xD7 tail in 12 of 17 input mappings and stale
tails in 62 output mappings. Output-tail counts depend on reuse/cache state; 74
is this attempt's observation, not a universal expected count. Its shutdown also
logged a rundll32 DLL-initialization popup, so its strict ordinary-run gate is
false independently of the expected EOF failures. This is retained, not waived.

The fixed run passes both mapping and strict ordinary-run gates. Five hives walk
successfully, all baseline payloads remain exact, and input disk slack remains
0xD7. Both complete allocation scans cover 318 directories and 6749 files after
the run. All 2,127,616 inherited reserved-cluster marks retain their exact positions.
The fixed run has no new popup, application event or unexpected warning/error.
These results support the next [isolated physical trial](HARDWARE-NEXT.md); no
physical deployment or new release qualification occurred.

## Fixture and workload

Both children share a new immutable parent derived from the pre-INF pair 004
fixture. This avoids the known 0088 post-install miniport checksum failure before
the filesystem probe can run. Miniport 0096, display 0097, startup, test executable,
input data and registry are identical between the pair; only FATX changes.
The inherited synthetic PCI resource model, two audio failed-install flags and
reserved low clusters are diagnostic fixture properties, not physical results.

The seventeen logical file sizes are 1,2,511,512,513,4095,4096,4097,8191,8192,8193,
65535,65536,65537,131071,131072 and 131073 bytes. Within EOF they contain a distinct
deterministic pattern. Remaining bytes in the final 64 KiB allocation cluster are
deliberately 0xD7. Page-aligned EOF has no tail within the final mapped page.

The no-CRT NT5 executable first opens actual read-only file mappings. It checks
every in-file byte and the final 4 KiB page's remainder, then verifies normal
ReadFile contents and EOF. Eight rounds recreate seventeen output files, change
their contents, write in 997-byte chunks, flush, close, reopen and map them. This
exercises 153 mapping checks and 136 create/replace/flush/reopen cycles. It does
not emulate paging calls in a host harness or use debugger intervention.

The log is exclusively created, records each individual check, and cannot be
reused by another invocation. Expected old-driver tail mismatches do not prevent
a normal restart; API/content failures stop the probe and cannot qualify. After
completion it allows two minutes for shell startup, then requests an ordinary
Windows restart. The supervisor launches once, observes offline/return, and
closes only that owned emulator. Dashboard return alone is not a pass.

## Cold checks

`audit.py` reads the closed image through a temporary read-only qemu-nbd Unix
socket. No kernel block device is attached. It checks the complete log sequence,
all 34 input/output contents, persisted payload hashes, five registry hives,
original input slack, and event-log records beyond the pre-run boundary.
Known recurring historical HID/Ftdisk events are allowed only on exact content
match. New popups and unexpected errors fail the ordinary-run gate.

`allocation.py` captures the full reachable F: directory tree and FAT for the
existing challenged allocation analyzer. It cross-checks its read transport
against the established qemu range reader, checks chains/ownership/orphans and
closes the owned export. Bad-cluster marks inherited from the high-allocation
fixture are synthetic reservations; compare their positions before and after.
Payload contents, mapping correctness and allocation consistency are separate
checks. Reports retain the negative control rather than turning its expected
mapping failures into a filesystem pass.

## Reproduction and limits

Build with PowerShell 7 `Build.ps1`, then run `review.py` with the project Python
and owned NT5 export archive. Staging and cold tools use WSL Ubuntu, qemu tools
and the pinned offline hivex runtime. `prepare.py` verifies the immutable parent,
stages unused child/seed names and refuses to overwrite them. `Run.ps1 -Case old`
and `-Case fixed` use the existing emulator lease. Run each `supervise.py` with
the emulator FTP credentials in environment variables, never committed config.
Use new attempt identifiers and unused artifacts for a repeat; do not relaunch
these completed attempt IDs. Exact payload/fixture hashes are in the manifests.

These are bounded serial API and persistence checks. Concurrent mapped-file
truncation, memory-mapped writes, arbitrary PnP stop/remove, long-duration stress,
higher video modes and physical hardware remain separate gates. No performance
conclusion follows from this functional emulator comparison.
