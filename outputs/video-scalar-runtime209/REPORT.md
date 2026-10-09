# Scalar UC-store comparison209: closed, no hardware speed benefit

The matched physical OFF/ON pair passed the scoped display checks, including
actual execution of the scalar stores. It did not demonstrate a hardware speed
benefit. Keep XWN_UC_STORES OFF; neither trial is a promoted installation or release.
The controller restored normal startup FIRST and readback-verified the original
FATX0101/video0093 display and SYSTEM baseline after each trial.

## Controlled inputs

Fresh208 builds use reviewed source tree
`4e335dc7a23b4fc058db597a1dded0c098af3cb1`. Only XWN_UC_STORES differs;
body clocks and text bounds are OFF both. The candidate uses the existing184
eight ordered volatile32-bit stores with original memmove fallback, alignment,
nonoverlap and wrap checks. No new copy algorithm, cache policy, mode or device
policy was introduced. Exact206 v11 probe/source,202 joined runner and201 helper
are reused byte-for-byte. Candidate fast-row/byte counters establish actual use;
the control has zero fast coverage.

Both new standalone emulator fixtures cold-check clean before launch:319
directories,6,716 files,320 directory clusters, zero errors/orphans, five parsed
hives and exact payload/provider/startup checks. No synthetic null bindings were
added. Fresh standalone E: run locations preserve existing backing chains, the
C:20GiB guard and projected clone/headroom checks. Resource refusals are retained;
no busy lease was bypassed and no guest was duplicated.

## Physical result

Control launched2026-10-09T23:25:20.050440Z; candidate launched23:31:27.045580Z.
Both completed and returned to dashboard. Combined controller sessions80707 and
87898 are CLOSED. Runtime geometry matched1024x576x32 at60Hz.

| Operation | OFF median ms/op | ON median ms/op | Elapsed reduction |
|---|---:|---:|---:|
| Fill | 2.060440 | 2.086231 | -1.25% |
| DIB upload | 2.467105 | 2.495840 | -1.16% |
| Unchanged readback | 0.974659 | 0.972132 | +0.26% |
| Overlap right/down | 2.467105 | 2.471170 | -0.16% |
| Overlap left/up | 2.669039 | 2.707581 | -1.44% |

All five raw samples per operation remain in physical-pair-review.json. The
candidate's first unchanged-readback sample1.655629ms/op is retained. Five
within-boot samples are not independent boots; OFF preceded ON. These small
differences do not establish a causal regression, desktop FPS or a speedup.

Each boot passed265 prior copy checks,200 owned-window readbacks,25 timed loops,
50 prior whole-scanout comparisons plus2,129,920 new text RGB pixel comparisons
and65 new whole RAM/scanout coherence comparisons. All13 text cases passed,
including opaque backgrounds, decorations, rotation, clipping and Unicode.
The four known hardware wizards were handled by the recorded helper without
disabling devices; helper join, actual5100ms idle and exact measurement SetupAPI
bookends passed. Normal restart and one EventLog6006 were recorded per trial.
Ten before/after structural hive checks, protected/provider/helper/payload checks,
typed policy checks and exact baseline restoration passed.

Both scoped results PASS. Strict whole-boot qualification remains FALSE for the
documented inherited pre-measurement Ftdisk49; there were no application events,
measurement errors or popup failures. The warning is not waived. This kit does
not perform a full physical allocation/all-file-content audit, dump recovery,
new-mode qualification or release qualification.

## Ordinary emulator result

Control79764 and candidate73411 are CLOSED. Both pass the same pixel/workload,
helper1/2/5 join/idle/bookends and normal shutdown/dashboard checks. Full cold
allocation is clean:324 directories,6,727 files,325 directory clusters, zero
errors/orphans; five hives, protected inputs and typed policies pass. Strict
whole-boot qualification is FALSE solely for inherited Ftdisk49.

Emulator upload/fill/overlap median reductions were about12–19%, while unchanged
readback worsened9.4%. Those results do not predict hardware throughput; the
physical pair above is the relevant result for this copier choice.

## Review and preservation

The recorded evidence review passes316 source/input/closure pins. Text/lifecycle
parser tests reject21 malformed logs; row-parser tests reject18 invalid cases.
Build/import/instruction checks pass. Historical184 host row tests are attributed
to their original run, not rerun here. The initial lease refusal and incorrect
full-binary-identity host assertion remain preserved; only PE timestamps/checksum
account for the fresh OFF binary difference from205, with no deployed edits.

All owned209/208 sessions are CLOSED. Never relaunch or recollect these case IDs.
Original0088 rollback, immutable0.1.0, physical0101/video0093 and all187/204/206
failed or closed evidence remain preserved. Independent device chats retain
separate branch ownership and emulator-only work; this chat sequences hardware.
