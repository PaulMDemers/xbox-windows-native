# FATX dump mapping removes the remaining strict boot-event failures

2026-10-07. The fresh matched ordinary emulator comparison is CLOSED and
cold-audited. Candidate0103 passes this bounded strict regression; control0101
still fails Ftdisk44/error4 and49/error3. Neither result is physical qualification
or proof that a crash dump can be written and recovered.

The prerequisite trace is committed as `df24162`: candidate0102 HAL successfully
handles dump-path usage, then FATX rejects the actual kernel query0x9003b with
C0000010.0103 implements that demonstrated missing paging-file contract. It
does not suppress an event, alter services, disable dumps or change device policy.
See DESIGN.md for caller restrictions, map lifetime, byte-offset construction,
allocation bounds and ownership. The full source tree is
`3f7316b6079e28eab45c07d8abdf720b118aa90f`.

Fresh, matched RosBE FATX binaries:

- Control: `a35d963cf4683833e107f28880a48144616355668940635d2f7eb85fa5c2927d`.
- Candidate: `247246b61f6b2f6bee25423860b8b3800290e84e405186efa69785b1609213b3`.
- Both use HAL0102 `7c6a3bfb9b6794c3b6fbce95fb76dc57d003843c19512b3ddb186604f668ed08`
  and unchanged video0093. Exact imports match owned kernel/HAL exports; checksums
  and resident function identities were reviewed. Builds retain the20GiB guard.

| Observation | control001 | candidate001 |
|---|---|---|
| Launch UTC | 10:21:22 | 10:26:01 |
| Dashboard return UTC | 10:23:45 | 10:28:33 |
| Appends / allocation shrinks / reopens | 792 / 32 / 132 | 792 / 32 / 132 |
| Exact cold result files | 11 | 11 |
| Normal shutdown count | 1 | 1 |
| Full allocation | clean | clean |
| Hives / protected hashes | 5 parsed / matched | 5 parsed / matched |
| New warning/error events | Ftdisk44,49 | none |
| New application events | none | none |
| Strict bounded qualification | FALSE | TRUE |

Each allocation audit found323 directories,6765 files,324 directory clusters,
zero errors and zero orphans. HidServ remained running4/0/0 at both helper
boundaries. No debugger or UI action was used. `pair-review.json` verifies the
same source/build flags, helper, initial hives, backing parents, startup and HAL.
Only FATX differs among protected files. Frozen scripts, raw reports, retained
closed disks and exact readback results are verified by `verify-evidence.py`.

All four before/after registry observations preserve CrashDumpEnabled3,
LogEvent1, AutoReboot0, Overwrite1, the dump-file path and C:\pagefile.sys96/192
configuration. All four cold pagefile maps match:96MiB,1536 clusters. The first
64KiB should map to volume-byte offset140436013056, followed by a zero pair.
This independently parsed offset is above128GiB. The additional five-check
ASan/UBSan host suite explicitly verifies widened offsets and signed-overflow
rejection. It supplements the4,032-check primary suite; it does not test the
dump miniport's large-LBA write path.

The new runtime-kit generator had two prelaunch adaptation mistakes (an
unmatched newline and an overbroad source-list replacement). Both were caught
by reading the generated scripts and corrected before fixtures/preflights or
launches. Existing frozen sources were never rewritten. The pair verifier's
first WSL invocation omitted the owned hivex library path; rerunning with the
required read-only runtime environment passed. No guest run or collection was
repeated, and no failure gate was relaxed.

## What remains

A NEW bounded debugger child must capture the successful output pointer and
terminated extent bytes, match them against the cold oracle, and verify the
NT5 caller retains the expected map and returns success. The ordinary passing
case must remain separate from debugger evidence. Then assess a disposable
controlled crash-dump write/recovery test, including the observed large offsets
and exact containment of changed disk regions. Do not equate clean boot events
with working dump recovery or a solved physical corruption report.

Physical0101/video0093,0088rollback and immutable0.1.0 remain unchanged. The
physical111 non-ASCII bytes and unknown first restart method are unresolved;
the intentionally interrupted111-zero/109-correct emulator result is separate.
