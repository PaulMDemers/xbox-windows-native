# 733: batched setup-prefix readback

Prepared2026-10-27. Kernel-context diagnostic on the1.6; no native handoff or
Windows. This compares batch-write/ordered-read behavior with723's interleaved
write/read probe. It stops before CR22/CR33 data writes and before geometry.

## Why this test

731 established plane-dependent CR22 readout;732 showed that unknown CR22 write
behavior prevents using a fixed FF check as a self-contained programming proof.
The full recipe is still not admitted. Instead, this diagnostic uses exactly the
11 MMIO/four CRTC prefix values already exercised by723/724/725. All15 writes
occur before the first readback, followed by the original ordering of the first
15 setup checks. The first mismatch short-circuits further forward reads.
Earlier probes read immediately after each write. This test asks whether a value
changes or a failure becomes visible by the deferred readback point.

This is deliberately a prefix comparison, not an exact replay of708/709: CR22 and
CR33 writes are absent, context is kernel, and instrumentation changes timing.
A passing prefix cannot prove that original full phase4 or later modesetting works.
A failure identifies the actual register, expected value and observed value in
this probe only. No functional guard, mode table or driver has been changed.

## Admission, recovery and reporting

Kernel720p mode and every framebuffer page are independently checked. Actual
critical CR0/3/4 and flags are recorded separately from preparation. The probe
requires the known prefix baseline, GR04=0, CR22=FE, CR33=11, SEQ1=1 and unlocked
CR11 before any data write. It never selects plane3 to force a check to pass.

The admitted sequence blanks using the previously exercised SEQ1/output-gate
operations, unlocks, executes the prefix, then checks all11 MMIO and four CRTC
values in order. It restores saved CR19, saved680630, output gate4 and savedSEQ1.
These are the same recovery writes used by723/725. It does not write CR1b85,
repeat CR1b05, write CR22/CR33, mask a mismatch or reconstruct firmware state.

Every final byte is compared with its actual saved value. In particular, CR1b05
may remain instead of saved85; that is recorded as cleanup mismatch, never called
restored. The independent forward_status survives cleanup or selector failure.
All20 cleanup comparisons have distinct mask bits. Selectors and captured flags
are restored before kernel/file APIs. The retained owned720p framebuffer and the
existing kernel report path avoid depending on an unobservable RAM-only result.

Seven exclusive E-only reports are intended, each flushed and reread.76 raw words
include all saved, checked and final values; see schema001.json. Green means the
prefix AND exact cleanup checks passed. Orange means forward-check or cleanup
mismatch, red a refusal/other setup failure, magenta failed durable reporting.
The status picture lasts15seconds then requests firmware return to UnleashX.
An automatic dashboard return is not a Windows shutdown. If black/held, record
what happened before requesting a reset. No startup hook is installed.

## Validation

Fresh nxdk build with pinned SDK and projected20.15GiB host/WSL reserve passed.
55 actual-COFF cases cover all15 first-failure locations, all20 cleanup bits,
CPU/baseline/blank/unlock/selector refusals, flags and alternate CR3. Dynamic
access checks prohibit unlisted writes, extra ports and CPU-control writes;
RAM guards restrict writes to result/stack. Deferred checks require all15 writes
already attempted. Full result arrays, first failure and cleanup masks checked.
Independent result-schema review passed those55 cases and rejected8 corruptions.
2353 compiled framebuffer-layout cases passed. Probe/main/layout nonrelocation
instruction bytes match linked PE and XBE. Modeled timing is not hardware timing.

No compile/model/review failure. Source-only reuse; no closed runtime reopened.
Preparation included unsuccessful filename lookups for724 prepare.py/host.py;
actual existing build/source files were then read. New web queries did not supply
a verified NV2A CR22/CR33 full access/restoration contract; no firmware acquired.
No full-mode or acceleration promotion. See stage001.json and NEXT.md for state.

## Physical result: CLOSED

One accepted launch2026-10-27T20:06:58.712475+00:00. User observed "Orange and
back at the dash" with automatic return and no manual reset. Seven reports
collected once with double-read equality. audit001 passed source/build/stage,
allocation, schema, report-order and unrelated-directory checks.

The aggregate and forward status are both0x7338: a forward check rejected.
All11 MMIO and four CRTC writes were attempted. The first14 checks matched;
check15 (zero-based14), CR1b, expected05 and observed85. There was no earlier
mismatch. The680630 forward read was2. Thus85 was observed before recovery,
without a preceding restoration of680630 to3 in this probe. No CR22/CR33 write
or readback check from the full recipe was executed.

Cleanup mask0: all20 full saved-state comparisons matched, including final
CR1b85, CR1951,6806303,SEQ1=1,GR04=0,CR22FE andCR3311. All three index selectors
and flags restored. Actual critical CR0/3/4=8001003B/0000F000/00000610;
entry/critical/restored EFLAGS=246/46/246. Cleanup succeeded; it did not cause the
orange result or erase the forward rejection.

Retained723 comparison: the11 saved MMIO values, four saved CRTC values and
actual critical CR0/3/4 match733.723's immediate CR1b read and final read were05;
733's deferred and final reads are85. EFLAGS condition-code bits differ (723
286/86/286 versus733246/46/246); both preserve incoming flags and clear IF in
the critical section. Readback scheduling and instrumentation differ, and these
are separate runs, so this is not proof that delay alone causes the difference.
See comparison001.json for evidence identities and limits.

The prior729 observation after680630 restoration remains valid for that run;
733 now shows that restoration is not required to observe85 in this kernel
prefix context. Bit7 meaning and a valid CR1b programming predicate remain open.
Do not replace full-byte validation with an inferred mask or claim708/709's
first failure is proved. No mode-switch, Windows1.6 or acceleration qualification.

Console is at UnleashX; no hook, owned host process or VM.733 is CLOSED; never
relaunch/recollect/parent it. No transport/collection/audit failure occurred.
A follow-up documentation lookup for723 REPORT.md was absent; comparison used
its retained, audited raw reports instead. All earlier failed evidence remains.
