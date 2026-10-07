# Aligned installer writes remain intact with coordinated GDI activity

7 October 2026 UTC. The matched control and drawing-enabled first-install
diagnostics both passed. The actual post-copy SetupAPI warning starts at 270225
in both cold files, matching the physical anomaly's logical offset. All 220 bytes,
including the first 111-byte prefix, match the expected emulator warning. The
physical corruption was not reproduced and no filesystem fix follows from this.

| Case | Mode | Launch UTC | Dashboard return UTC | Completed drawing cycles | Result |
|---|---|---|---|---:|---|
| 001 | Control | 04:28:02 | 04:31:08 | 0 | PASS |
| 002 | Drawing | 04:33:32 | 04:36:31 | 4688 | PASS |

## Coverage and verification

The drawing worker completed its first frame while observed SetupAPI EOF was
268485, before the target warning at 270225. It remained active across each
30-second sample interval, and was stopped and joined before the normal-restart
request. The final worker exit code and error counter were zero. The control
created the same window and GDI resources but completed zero drawing cycles.

| Relative sample time (ms) | Drawing cycles completed | Observed SetupAPI size |
|---:|---:|---:|
| 0 | 2 | 268485 |
| 30000 | 816 | 271385 |
| 60000 | 1813 | 271385 |
| 90000 | 3686 | 271860 |
| 120000 | 4687 | 271860 |

One additional cycle completed before the worker joined. Readiness was recorded
after the first cycle; these observations bracket target file growth during the
worker lifetime. They do not prove overlap of individual I/O/drawing calls,
pixel correctness or GPU acceleration, and these timings are not a performance
benchmark. The drawing window can be occluded by installation dialogs.

Both runs appended 5,300 ASCII bytes, preserving the original log and padding.
The exact post-copy warning remained at sector offset 401 and 4 KiB offset 3985.
Its first 111 bytes end at270336. The same FAT chain maps this location to emulator
LBA290163071; the saved physical second-boot capture maps it to292691839. Matching
logical offsets does not make the disk sectors, allocation history or controllers
identical, nor establish the physical mapping at the instant of the first write.

Both helpers performed the exact successful GPU Finish, same-process restart No,
and command-line-identified emulator placeholder Cancel once. Each install queue
was idle before restart. GPU ConfigFlags 0, class 0001, XboxVnt5, exact oem2.inf,
Start 3 and display binding were checked separately from normal shutdown evidence.
EventLog recorded one normal shutdown per case. No new unexpected warnings/errors,
popup records or application events appeared. Identical inherited SCM 7000 and
Ftdisk 49 records retain their explicit diagnostic classification.

All selected payload/runtime/driver/boot hashes matched, and all five registry
hives parsed structurally. Each preflight had 322 directories, 6739 files and 323
directory clusters; each post-run scan had 322 directories, 6745 files and 323
directory clusters. Both full F allocation audits found zero errors or orphans.
The known reserved/bad-cluster region is inherited fixture topology. These are
selected binary checks, not a repeat of the physical 3,439-binary/nine-hive audit.

## Reproduction and evidence

Both cases are fresh children of the immutable fatx-install-alignment001
pre-install fixture, never children of a completed run. They retain the padded
log, all five hives, startup, INF, FATX0101 and video0093. The same reviewed helper
replaces xwnidle/probe.exe. The only differing staged payload is the one-byte
xwnidle/drawmode.txt value 0 or 1; all protected hashes match.

Helper SHA256:
`0ee803b0cd20c214caf4b532f53c26a493cb421159904212c40d2440ee588668`.
The original 8,985-byte matcher/action prefix is unchanged after CRLF normalization;
ui-preservation.json records this separately from the new entrypoint/worker code.
The worker uses ordinary FillRect, BitBlt and GdiFlush APIs with checked resources
and cleanup. Read-only log-size observations perturb timing and are diagnostic.
Build.ps1 uses the pinned RosBE compiler with warnings as errors; probe-review.json
checks imports and both dynamic exports against owned Windows 2000 DLLs. An initial
indentation warning stopped compilation and was fixed before either fixture was
staged; no failed build was launched.

Each qualification.json pins its cold audits, alignment, drawing, package,
allocation, launch and collection records. comparison.json pins both qualifications
and the mode distinction. verify-evidence.py checks the staged source/evidence
bytes and original UI prefix. Raw guest files/media stay private and ignored.

Both owned runners, supervisors and cold readers are closed. No physical access,
driver edit, recovery snapshot, tag change or automation change occurred. This is
UI-assisted emulator diagnostic evidence, not ordinary or physical qualification.
The hardware's 111-byte malformed prefix and first-reboot method remain unresolved.
NEXT.md moves to identifying the actual installer write request and buffer path,
with debugger observations kept separate from ordinary runs. Physical 0101/video0093,
normal startup, GPU registration, remaining device prompts, raw-C warning,
original 0088 and immutable 0.1.0 remain unchanged.
