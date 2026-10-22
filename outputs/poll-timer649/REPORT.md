#649 timer-path validation and elapsed-tick diagnostic

648 is CLOSED. Its second amber/off indication mapped to wait3, the second-pair
clear wait. It did not capture the failed wait's duration.649 tests the compiled
delay path, then adds two timer reads around each started wait. Video register
accesses, predicates, sample limit, requested delays, profiles and reset path are
unchanged. Extra reads and RAM bookkeeping still perturb timing.

## What the host checks established

timer_host.py executes exact retained648 wait_us/GetTimerTicks instructions in
fresh isolated Unicorn CPUs. Only IN is modeled. An independent rational and
binary32 nearest-even oracle checks the conversion.32 cases cover ordinary and
clamped arguments, rounding/precision modes, strict boundary,32-bit wrap,24-bit
wrap, backward jump and frozen timer. The same32 cases pass on the649 executable.
For normal modeled input,10us produces target35 and waits for a delta greater
than35. Callee-saved registers, stack and original FPU control word are checked.

The modeled32-bit wrap works. Modeled24-bit wrap or a backwards jump can yield
a large unsigned delta and return early. A frozen timer does not return within
the host instruction budget: unchanged wait_us has no independent loop bound.
These are model properties, not observed console failures. Actual timer width,
frequency, current FPU state and physical elapsed time were not captured. Source
uses3.579545 ticks/us and the boot source contains CLTS/FNINIT; neither constitutes
a live hardware reading. FPU state was changed only in isolated host test CPUs.

## Candidate and observable result

The adapter records GetTimerTicks immediately before and after each status wait,
using unsigned32-bit subtraction. This reads the same0x8008 port that wait_us
already uses; no new video-status read or control-register modification is added.
Per-wait fields retain first/last status byte, samples, transitions and completion,
plus raw begin/end/delta. All detailed fields are RAM-only, not durable receipts.

On error22 the diagnostic shows three eight-second indications, separated by
two-second dark pauses: result class (red/green), failed wait (same648 mapping),
then the failed wait's unsigned timer-delta category. The third pattern is:

| Third LED pattern | Raw unsigned timer delta |
|---|---|
| Red/off | Less than100000 ticks |
| Amber/off | 100000 through2999999 ticks |
| Green/off | 3000000 through36000000 ticks |
| Red/green | Greater than36000000 ticks; long or discontinuous/wrapped reading |

An invalid phase produces no third pattern. Under the source's frequency
assumption, these thresholds are roughly28ms,0.84s and10s; they are not verified
wall-clock measurements. Green/off in the THIRD slot does not mean boot success.
A category alone cannot distinguish counter discontinuity from real elapsed time.
In particular24-bit wrap can produce the large-delta category. A missing indication is
inconclusive; absence is never permission to retry a launch.

Non-error22 results keep the initial eight-second class indication and original
continuation/reset behavior. Each LED transaction is attempted once. The original
delay can still hang if its underlying timer freezes; no new independent timeout
or functional timer fix has been inserted. A watched attempt may need user reset
if it remains offline; do not make unattended automatic recovery claims.

## Validation and provenance

Build001 uses pinned633 tree70c0a6c5aff82537f489e7d18410d5980fa797a7, GCC12 SHA
e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4, and the unchanged
mode3 flags. Private C:/xwn649/build001/default.xbe is302608 bytes, SHA256
845848b0f517ce3608a429310560a3d9529da8c43dc94a25e2276a70aeed92bc.
Removing native insertions recovers original633 bytes; reversing adapter additions
recovers original source text. Profile text/rodata and timer/library object text
match633 exactly. New source/object/temp files are on C with20.02GiB output/WSL
backing-volume guards. No VM, disk image or historical deletion was used.

- 44 ASan/UBSan differential adapter cases preserve original callback sequence
  and result state, validating new elapsed-tick fields through modeled wrap.
- 516 host LED cases cover phase/delta boundaries and every diagnostic-write failure.
- The retained633 host suite passes235552 assertions against the instrumented code.
- 180 linked-wrapper cases verify trace indexing, LED sequence, ABI and reset path
  with explicitly modeled setup result, SMBus send and delay.
- 10 linked-adapter cases execute actual timer-read instructions with synthetic IN
  values and modeled video callbacks; six failure phases and boundary cases pass.
- 32 exact compiled timer cases pass for both retained648 and new649 images.
- Controller host tests enforce one SITE for accepted and uncertain launch replies.

No model establishes physical status semantics, scanout progression or boot
reliability. No timer defect, adapter defect, prior645 cause or functional fix
has been established. No live-switching, other-revision or acceleration promotion.
Read actual preparation/stage/launch records and NEXT.md before physical actions.

Preparation captured28 selected baseline files with repeated exact readback.
Staging wrote only the unique E:/Applications/XWNTimer649 owner.json and XBE,
then verified both. Normal720p/startup remain exact; no hook or dashboardC access.
No SITE has been sent. Three-pattern watch readiness is pending. Build/staging
processes exited; existing physical lease retained. Detailed state is in the
actual preparation001/stage001 records, not an assumed boot outcome.
