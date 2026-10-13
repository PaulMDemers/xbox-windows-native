# Primary-copy349: functional checks passed; large-copy coverage failed

The matched pair is **not qualified**. Both fresh emulator runs produced the
expected pixels, completed the audio workload, restarted normally, exited the
host orderly and passed cold integrity checks. Candidate348 did not satisfy the
new full-requested-fast-byte coverage requirement for the largest overlap
copies. No physical access or deployment occurred.

Control launched October13 16:57:20UTC and returned17:02:56UTC; candidate
launched17:07:37UTC and returned17:13:47UTC. Both cases are closed. Never
relaunch, recollect or parent from either executed runtime. Each used a fresh
child of the never-executed339 stock-E seed, the same348 probe and inherited
emulator-only device policy. Only XWN_PRIMARY_COPY differed; profiling was ON
in both. See pair-input-review.json and each fixture/frozen/launch/closure.

## Actual coverage failure

| Requested overlap | Fast calls/op | Engine fallbacks/op | Fast bytes/op |
|---|---:|---:|---:|
| 256x128, both directions | 1 | 0 | 131072, complete |
| 640x360, both directions | 1 | 0 | 921600, complete |
| 960x540, both directions | 8 | 5 | 2067564 of2073600 |

The6036-byte deficit occurred in all ten largest intervals across five samples.
All independent drawing/pixel checks passed. This establishes incomplete
fast-path coverage, not corruption. Counter totals do not identify the actual
rectangles, bitmap/primary operands, clipping or rejection reason. The1509-pixel
equivalent is not evidence of a cursor or window cause. Preserve the full-byte
gate as FAILED; do not substitute a percentage threshold.

coverage-diagnosis001.json independently reconstructs the observed counters
from the captured logs. Its phase projection is explicitly diagnostic, not a
replacement qualifier. Emulator timing changed most in the **unchanged upload
body**, so neither that difference nor the total wall difference establishes a
causal optimization benefit. Selected CopyBits body includes the engine and
fast path; it must not be labeled engine-only. No hardware speedup is claimed.

## Functional and cold evidence

Both cases completed five drawing samples, the original copy/DIB/text/window
checks, six captured audio phases, audio API/device identity and joined workers.
Each reported one normal shutdown and orderly host exit0. Cold allocation was
341 directories,6809 files,358 directory clusters,zero errors/orphans. Five
structural hive checks, protected hashes, startup/device policy, SetupAPI and
event-history checks passed. The sole strict event failure in each emulator
run remains Ftdisk49 on HarddiskVolume1. It was not suppressed or waived.
Physical347 Srv2013 is separate evidence; no console partition was accessed.

## Preserved parser and closeout failures

The old344 decoder expected PHASE344 immediately before LARGE_TIMING. The new
probe inserts its66-line PRIMARY348 block there. Both original audit.json and
closure.json preserve that original parser failure. phase349_analysis.py first
validates the entire new packet and its exact placement, then projects it away
for the unchanged344 decoder.1051 actual-log mutations are rejected; five
event/integrity/setup/audio/exit gate controls still fail. Separate
log-protocol-qualification.json records reevaluation with the original eight
gate expressions. It does not rewrite the audit. Control scoped result is TRUE;
candidate remains FALSE because actual primary-byte coverage fails.

The first final-review.py wrongly required all corrected samples to pass before
recording a closeout. It failed on candidate sample0 and wrote no output.
closeout002.py instead verifies evidence integrity while explicitly retaining
the failed experiment. It rehashed both178-input freezes, prepared fixtures,
private captures, matched drivers, probe, supplemental protocol pins and22
host-test private files. closeout002.json records the original failed reviewer
hash and error. Evidence integrity PASS is not experiment qualification.

Preparation's original unwritable WSL work-root refusal occurred before fixture
mutation. prepare002 uses private build staging with unchanged20GiB guards and
verified raw/QCOW equality; the original script/refusal is retained. The earlier
weaker host001 byte pattern and stronger host002 result are both retained in348.

Staged byte review found doubled CR line endings in the executed, frozen
prepare002.py. Its bytes remain unchanged and match both original freezes.
A file-specific whitespace-check exception retains that evidence; future
generators should use explicit byte writes. No runtime check was waived.

All owned sessions are closed. The physical E driver, normal startup, original
F rollback and immutable release tags remain unchanged. No release promotion.
