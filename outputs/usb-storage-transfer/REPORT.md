# Correct data, missing QCOW mappings after forced emulator termination

The forced-stop experiment stored the correct status, payload and exit bytes in
the raw QCOW child, but their persisted L2 entries were zero. Logical readers
therefore returned stale parent data. A fresh sibling using an orderly emulator
exit retained the mappings, exact payload and exit record, consistent allocation,
and five fully parseable registry hives. This identifies a recovered-image
failure in the forced-stop harness; it does not establish a FATX, ATA or XID
producer defect or qualify guest flush durability.

Both experiments are closed. Neither completed a normal Windows restart: the
unchanged probe held restart after a device-setup timeout. No physical-console
access, driver change, baseline replacement or integration was performed here.

| Evidence | emu001: forced process termination | emu002: HMP stop, then quit |
| --- | --- | --- |
| Closed UTC, 2026-10-11 | 00:31:36.656 | 00:47:15.564 |
| Matched DMA/backend request pairs | 1,226 | 1,203 |
| DMA and backend completion status | All zero | All zero |
| Missing, capped or pending captures | None | None |
| Saved L2 mappings for three probe files | All zero | All present |
| Logical cold payload | Stale parent bytes | Exact 2,226 bytes |
| Logical cold exit record | Stale bytes | ASCII 5, space, CRLF |
| Allocation scan | 12 orphans; broken WMI chains | Consistent; zero orphans |
| Full hive traversal | All five parse; unchanged parent contents | All five parse; updates retained |
| Selected written bytes equal cold image | Mismatches in all eight targets | Exact in all eight targets |
| New warning/error events | Empty recovered delta | Ftdisk event 49 |
| Guest normal restart / ordinary qualification | Failed / false | Failed / false |

For emu001, the expected payload is intact at raw child offset 34,922,496, SHA-256
`b75a944b0372b5c98bdeda88cdbe594de66f63e897522d58ccb813ac05c5cdf9`.
The status and exit bytes likewise match backend submissions in the raw child.
The absent mappings explain why independently reading the logical image yields
old bytes despite successful backend completion. See
[mapping evidence](emu001/qcow-evidence.json),
[submitted records](emu001/submitted-records.json), and
[cold comparison](emu001/transfer-cold-comparison.json).
Recovered submitted records are explicitly separate from logical cold files.

In emu002, the corresponding mappings are nonzero. All observed successful final
writes to the status, payload, exit and five hive ranges match cold readback;
there are no overlapping in-flight writes in those selected ranges. The comparison
covers 274, 2,226 and 4 file bytes, plus respectively 130,048 / 18,432 / 3,072 /
2,560 / 3,072 written bytes in SYSTEM / SOFTWARE / DEFAULT / SAM / SECURITY.
Untouched bytes are excluded from that write comparison. Independent qemu-nbd
and qemu-img views agree on full files, hives, FAT and the 148 selected clusters
per case. See [mapping evidence](emu002/qcow-evidence.json),
[cold comparison](emu002/transfer-cold-comparison.json),
[full audit](emu002-review.json) and [hive/event details](emu002/details.json).

The orderly-exit harness itself reported a TCP connection reset after sending
`quit`. That error is retained in [host-close.json](emu002/host-close.json) and
[emu002-failure.json](emu002-failure.json). HMP acknowledged `stop`; the owned
process then exited with code zero and the runner's finally block did not kill
it. [Cleanup](emu002/cleanup.json) and the separate
[closure interpretation](emu002/closure-interpretation.json) establish this
distinction. The observer's generic watchdog wording does not override actual
process cleanup. Current close-host.py accepts reset only after quit; Run.ps1
also requires exit code zero. These post-run fixes were not used in emu002;
its exact prelaunch scripts remain frozen in emu002/source.

The remaining limits matter. Neither trace contains IDE FLUSH CACHE (0xe7) or
FLUSH CACHE EXT (0xea), and the captured top-backend writes have flags zero.
The pinned emulator source marks new QCOW links dirty in its cache and flushes
cache state on block-device close; see [source contract](qcow-close-contract.json).
This control changed host closure, not Windows shutdown. It cannot establish
FlushFileBuffers semantics, power-loss safety, physical-disk durability or a
completed setup lifecycle. Ftdisk 49 keeps the strict event gate false in emu002;
its cold-integrity gate passes, but normal/scoped restart and ordinary-boot
qualification remain false. The empty recovered event delta in emu001 is not
evidence that no events occurred.

Three outstanding write buffers changed between endpoint snapshots: emu001 IDs
384/385 (two 64 KiB ranges, up to 644 and 36 changed bytes) and emu002 ID 431
(four changed bytes). None overlaps the eight selected cold targets. The traces
do not identify the writer or establish a causal link to an integrity failure.
These observations remain in each case's phase-differences.json; they are not
discarded because the control passed. Endpoint agreement also cannot exclude
transient changes between snapshots.

Guest/storage binaries were unchanged from ccd210fa2aac3fb24f3223aa66036096fd0ecbf0.
Both fresh siblings used closed first-boot parent SHA-256
`6de11f0ce947138eddbabfa503836f3bb4b7eb51905795238a489f1236584f97`,
the no-XID probe and a single phase-two launch with 64 MiB RAM. The probe performs
75 writes, totaling 2,226 deterministic bytes, and requests a flush after each.
No debugger or guest-memory modification was used. The emulator timing is
instrumented; these are diagnostic runs, not ordinary-boot qualifications.
The successful build reconstructs all 11,340 baseline source pins at xemu
e72e76bd1f12ce45c6c63b4196c6918ea2cc705d, then changes two host capture sites and
adds one header. Executable SHA-256:
`5070031bedd5e58649ffb74aac53f12e06482db143d01d00a466d0d79310fd36`.
Compiler/container identity, flags and patch hashes are retained in build.json,
DESIGN.md and instrumented-source-pins.json. Four unsuccessful/interrupted build
attempts precede successful attempt005; all closures and failures remain.

All eight earlier closed images and both new images are preserved. Earlier
buffer-trace SYSTEM/SOFTWARE parse failures remain failures; this experiment
does not retrospectively explain every older invalid hive. Raw disks, guest
media, traces, buffers and binaries remain private on E:. Source, compact
indexes, exact hashes and derived evidence are the reviewable deliverable.
The next bounded investigation is described in [NEXT.md](NEXT.md).
