# 218: stock instance probe calibration

The query-only probe is calibrated in ordinary emulator case epath007. All four
20KiB captures and a1152-byte report were recovered from the intended E: folder;
independent comparison agrees with the guest. The CPU window was stable but all
zero; PRAMIN was stable with563 mismatched words. This is uninformative physical
alias evidence, consistent with the explicit separate-RAMIN emulator limitation.
It grants no NT5 ownership and qualifies no GPU context switch or copy.

The E: allocation audit passes, every original E: file has the same hash, and
exactly five probe files were added. The full F: allocation audit remains
320 directories,6719 files,321 directory clusters, zero errors/orphans. Five
hives parse and all protected-file hashes match. This was a stock-kernel app,
not a Windows shutdown test. The app requested a stock restart; the emulator
closed at the host bound, so a dashboard return is not claimed.

See review218.json, e-audit007.json and emu-epath007/audit.json for actual gates,
input hashes and observations. The pinned NXDK revision is58427c0, xemu685f24e3,
BIOS34f1c8de and original parentf50befc5. Build005 source is main005.c. Shared
SDK libraries were unchanged. The pure comparator passed98 checks over16 seeds.
Fresh app builds003/004/005 compiled their source and all outputs; their recorded
make clock-skew warnings are retained, not treated as incremental-build proof.

## Preserved failures and corrections

| Case | Actual outcome |
| --- | --- |
| correlation001 | No probe files; protected files, five hives and F allocation pass. Initial audit lacked C geometry; second lacked the existing hivex library environment; both failures retained before completed audit003. |
| correlation002 | Same absent files and clean cold audit. Explicit C boot entries were replaced only in an isolated fixture; this did not resolve the problem. |
| bootpath003 | Read-only debugger identified actual loaded image as\Device\CdRom0\default.xbe. Resident app prologue matched. This disproved the boot-selection assumption. |
| stack004 | Bounded read-only stack captured the stock firmware-return path and caller bytes; no failure cause inferred from the stack alone. |
| progress005 | Pinned resident progress array proved directory creation failed with Windows error123 before query or GPU reads. Cold disk unchanged; no files. |
| native006 | Native absolute file creation reached capture, but the stock F: writes damaged this disposable NT5 large-F fixture. Strict integrity FAIL, preserved. |
| epath007 | Same native app with output on fixed E: completed, with full E readback/allocation and F/hive/protected gates passing. |

main.c/build001 was never launched. main002.c used Windows wrappers with a
non-null DOS object root even for absolute native paths. main003.c added a
RAM-only progress array to identify the actual error. main004.c uses
NtCreateFile with RootDirectory=NULL, keeping raw NT status and CREATE_NEW
semantics; main005.c changes only the output partition/path to fixed E:.
No shared SDK, Windows driver, device policy or physical boot entry was changed.
The standard pinned SDK CRT may automount D:; no new F:/E: alias was added.

native006 changed the SOFTWARE hive and allocated clusters2679..2685, including
root-chain extension2679 and six unreachable new clusters. The other four hives
parse. No full file-content safety is claimed for that failed disk. The first
cold audit stopped at the SOFTWARE parse failure; audit006b completed and kept
all failures. Read-only forensic extraction recovered the report and raw files
from inside the damaged SOFTWARE payload, not from the requested namespace.
These bytes establish execution; they do not turn the failed case into PASS.

Independent cold mapping locates native directory cluster2679 at8187543552,
where the NT5 oracle expects8194416640: displacement-6873088. The inferred native
cluster1 is8012038144 versus NT5's8018911232. A legacy F: ending at LBA2^28 gives
exactly that native offset. This is an exact arithmetic match, not a captured
stock volume-length query or proof of its internal truncation producer.
See forensics006.json, forensic-recovery006.json, geometry006.json and
geometry-arithmetic006.json. Never boot or adopt the failed native006 disk.

## Physical boundary and closure

The hardware-facing build005 payload is copied/readback verified under private
artifacts/physical001. physical-plan.json specifies a NEW F: app folder and
small E: reports, with absence guards for both. The physical Xbox FTP timed out
on both readiness checks. No file was uploaded and no console app was launched.
The readiness question remains pending; do not infer console screen state.
Preserve physical FATX0101/video0093, original0088 rollback and immutable0.1.0.

All seven emulator cases are closed, all debugger captures resumed without
installing breakpoints, and no owned guest remains. Both original parents are
unchanged. Failed audit evidence and standalone retained disks remain private.
C: capacity was recovered by hash-verified offload of CLOSED standalone029/031,
with original paths retained as verified junctions. No backing chain moved and
the20GiB build guard stayed unchanged. The offload manifest records every file.

Other-device check-in is complete and pushed in161921a. Audio is experimental
emulator playback, PCI is SMBus support with pending-install shutdown failure,
USB is descriptor collection without a functional XID minidriver. No combined
integration or physical qualification occurred. See ../device-checkin217/REPORT.md.

Additional Git reconstruction checking initially rejected historical helper LF
blobs against working CRLF pins. That host failure is preserved in
commit-check001-failure.json. check-commit218.py verifies all438 actual working
pins and either literal Git bytes or exact LF-to-CRLF reconstruction, recording
each difference in commit-validation.json. No runtime hash was changed.
