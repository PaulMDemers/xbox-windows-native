#540: hold at the existing post-stack LED checkpoint

539 returned to dashboard without a watched sequence or persisted Windows activity.
Its pre-handoff packets match536 successes except timing and marker polls. They
do not establish whether Xromwell stack setup was reached. That gap includes the
context file's own flush/close, final comparisons, original state restoration,
paging/descriptor changes, relocation and real Xromwell early setup.

540 derives from the pinned, never-executed490 build artifact. It retains the
existing post-stack diagnostic instead of539b's removal. The only code change
replaces the five-byte successful return at0268001f with CLI;HLT;JMP back;NOP.
All sizes, copy lengths, offsets, entry/loader/setup code, IO and both marker
values remain unchanged. Four equal-length path strings and the section digest
also change. Inverse transformation reconstructs exact490. No compiler is used.

Expected watched sequence: amber at the earlier marker, then alternating red/green
from the existing post-stack marker. On marker success the processor intentionally
holds before continuing into Windows. A manual power cycle is required after the
observation, normally about30 seconds. This is a finite transaction count and
bounded marker polling, followed by a deliberate indefinite halt, not an automatic
return or a globally time-bounded console runtime. The user must be present to
observe and reset. No Windows workload or startup hook is installed.

A positive red/green indication supports arrival at the post-stack marker in
THIS instrumented run. It cannot diagnose539 retrospectively or establish boot
reliability. Amber or no change is ambiguous: early failure and marker failure
are possible. A red/green indication alone does not attest both transaction
completion statuses or execution of HLT. This limitation must accompany the
observation. Reset path and exact user report must be retained separately.

The original marker already disables interrupts within its bounded transaction.
No pending/error bits, mapping, firmware, functional driver or reset path are
changed before the intended terminal hold. The new CLI is at the deliberate
terminal endpoint. Inherited marker failure also halts; do not call that success.

Host testing executes actual marker/caller bytes with explicitly modeled SMBus
and TSC through success/busy/error/deadline outcomes and IF/DF combinations. It
stops before HLT, independently checks its loop bytes and the emitted LED data.
Earlier privileged code is statically decoded, not newly physically validated.
488's diskless synthetic payload remains a separate result, not real Xbox proof.

One fresh unique E:/Applications/XWNBoot540a launch only, after confirmed LED
watch/reset availability, exact stage readback and ten-file baseline checks.
No retry/control fallback. Preserve ordinary720p/startup and Xbox C exclusion.
On user reset/dashboard report, collect only this run and audit five hives/events.
No normal Windows shutdown is expected or inferred. Keep all earlier runs closed.
