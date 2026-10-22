#648 phase-specific vertical-blank diagnostic

647 is CLOSED. Its watched red/green indication is consistent with error22 in
that instrumented run, but did not identify which of six waits timed out.648
adds RAM bookkeeping to the existing sampled status bytes, retaining the same
address, predicates, loop limit, requested delays, video writes and reset path.
No pending bit is cleared, timeout enlarged, gate waived or video profile changed.

Each wait records expected bit, first/last byte, number of samples, byte changes,
bit3 changes and completion. The aggregate records started/completed waits and
the one-based failed wait. The trace resets at the beginning of apply and remains
RAM-only; it is not a durable console receipt. Per-sample bookkeeping and code
layout change timing. A future success would not establish an ordinary-boot fix.

The post-result indicator retains647's result-class mapping for eight requested
seconds. For error22 only, it then goes off for two seconds and displays the
failed-wait code for eight seconds before restoring automatic LED control and
taking the original reset path. The second pattern is:

| Second pattern after the dark pause | Failed wait |
|---|---|
| Red/off | Pair1, waiting for clear |
| Green/off | Pair1, waiting for set |
| Amber/off | Pair2, waiting for clear |
| Red/green | Pair2, waiting for set |
| Red/amber | Pair3, waiting for clear |
| Green/amber | Pair3, waiting for set |

The first red/green alone still means only error22. A missing second pattern is
inconclusive: LED transaction failure, invalid phase, missed interval or another
exit can prevent observation. The sampled bytes/counts will not be inferable
from the color. The console indicator is human-observed evidence, not a captured
hardware register dump. No extra status reads were added for instrumentation.

Build001 failed before compilation because source generation normalized original
CRLF bytes; the exact-source guard rejected it. Original sources/scripts remain
under candidate001 with hashes in build001-failure-review.json. Build002 keeps
the original native source bytes. Removing the native insertion recovers exact633
bytes; reversing adapter additions recovers original source text. No prior failed
build or runtime was overwritten/reused. No console launch during these checks.

Build002 derives from source tree70c0a6c5aff82537f489e7d18410d5980fa797a7,
with pinned GCC12 and the633 flags/mode3. Private binary:
C:/xwn648/build002/default.xbe,302096 bytes, SHA256
b55e84798b081421252a9852dc6c46b0e4a574deec876177f6a4d3b9f901198c.
New source/object/temp files are on C; projected20.02GiB guard checks the output
and WSL backing volumes. No VM, disk image or backing-chain move was involved.

Validation:

- 44 ASan/UBSan differential scenarios compare original and instrumented adapter
  callbacks and returned state exactly. Both modes, six failure phases, final
  allowed sample, first disallowed sample, delayed transitions, unrelated status
  bit changes, pre-write rejection and sync failure are covered.
- 52 host LED cases cover phase codes and each diagnostic-write failure. No retries.
- The retained633 adapter test also passes235552 assertions against this candidate.
- 100 cases execute the linked native wrapper with modeled setup result/phase,
  SMBus send and delay, checking indication sequences, ABI and original reset path.
- 10 cases execute linked adapter/profile instructions with synthetic callbacks:
  success, delays, all six timeout phases and two final-allowed-sample cases.
- The profile object's text and read-only data match633 exactly. The adapter text
  changes for bookkeeping; no assertion of byte-identical adapter code is made.
- The physical controller's accepted/uncertain launch cases enforce one SITE only.

These tests do not validate physical timing, input-status semantics or a boot fix.
See build002.json, compiled-wrapper001.json, compiled-adapter001.json, review001.json
and host001.json. Source pins are frozen; do not edit controllers after staging.
No automatic-mode, live-switching, other-revision or acceleration promotion.

Physical state: preparation captured28 selected before files with repeated exact
readback. Staging wrote only E:/Applications/XWNPhase648/owner.json and default.xbe
in a unique folder, then verified exact bytes. No startup hook or dashboardC
access. Normal720p remains unchanged. No SITE sent; awaiting a watched second
LED indication. Build and staging processes exited; physical lease retained.
