# 246: actual UI loans closed and reopened

The fresh emulator diagnostic closed UI frame admission at the pinned FreeLoader
entry. The real UI actor acknowledged loan=0 with BQL unlocked, completed its
100ms-budget GL fence with GL_CONDITION_SATISFIED, and kept admission closed for
298,488,700ns. The raw trace contains no new loan in that interval. The same actor
then acknowledged reopening and resumed ordinary frame loans. This establishes
a finite UI closure; shared renderer/display contexts and native GPU ownership
remain unqualified.

The actual UI context was 65537, thread 32308. Its last selected texture 26 was
a fallback texture already deleted by the preceding ordinary frame (live=0).
Actual bindings remained: texture2D=0, program=9, arrayBuffer=5,
elementArrayBuffer=6, drawFramebuffer=0, vertexArray=3, activeTexture=33984.
These IDs are scoped to this run/context. They are not a complete object
inventory or evidence that another shared context released its references.
The diagnostic neither cleared bindings nor deleted caches or display objects.

| Actual trace evidence | Result |
| --- | --- |
| Lifecycle events | 16,989 |
| Insert/remove/unlink/free callback chains | 23 complete |
| Preserved target hooks retired before final marker | 3 of 3 |
| CPU-stopped callback frees | 0; frees occurred while CPU ran |
| Natural surface flush | 1 complete |
| Completed UI frame fence/release chains | 2,162 |
| Accelerated / fallback frames | 1,908 / 254 |
| Completed loans before closure fence | 2,143 |
| New loans during acknowledged closure | 0 |
| Sync empty-surface returns | 0 |
| Shared-context retirement / native GPU ownership | FALSE / FALSE |

The same boot pinned actual Xromwell11100 and FreeLoader200a20 resident bytes.
Earlier preservation compared 3,072,000 bytes across three dirty surfaces using
the existing GL conversion/readback path and fences. This remains the same-path
oracle, not independent pixel reconstruction. Dirty flags/latest data at later
natural invalidation were not recorded: earlier preservation does not prove
that a subsequent draw was preserved by the existing disabled-download flush.
All GDB points were removed, memory mode0 verified and the guest resumed.

Windows restarted normally, returned to dashboard and exited through orderly
HMP stop/quit with host exit0. The CPU workload passed 65 allocations, 65 releases,
65 exposure refusals, 3,194,880 verified bytes and four joined workers. Its native
retirement probe still refuses UNMODELED_BUSY and NO_OWNERSHIP. Cold checks passed:
6,724 files / 320 directories / 321 directory clusters, zero allocation errors
or orphans, five structural hives, 28 selected protected files, staged files,
startup, device policy, SetupAPI/event history and empty application-event delta.
Sole Ftdisk49 type1 remains a strict failure. No ordinary, physical, all-file-
content, power-loss, repeated-boot or native acceleration qualification is claimed.

Candidate build001 SHA256:
feec01cc40efad36ef16232415c08a7bee1eb902948ae8f8798b061b6863e025.
It changes four source files relative to exact244/build005: UI gate/report,
NV2A QOM API, declarations and a renderer trylock loan observation. Every borrowed
source was restored. Native224/219/211 captured core, immutable239 seed and actual
device policy stayed unchanged; no synthetic null bindings or physical access.

The actual compiled helper passed O0/O2 ASan/UBSan tests: each exercised 2,304
fresh logic lifecycles and 256 joined actor races, including held-BQL, busy/live
loan, context/fence/error refusals and abort-versus-publication. These use explicit
GL/renderer adapters and do not replace actual GL runtime evidence. Causal host
parser tests passed 19 close cases and 20 lifecycle cases; intervention/guard/
closure/connection tests passed 54/72/25/12 checks. 1,140 frozen pins stayed exact.
The preliminary helper-test001 compile failure (missing test assertion macro)
and incomplete guard source-capsule setup are retained. Candidate binary was
unchanged by those harness repairs. Failed244 and successful245 remain separate.

The sole run nt5-phase246-preserve001 is CLOSED; never relaunch or recollect it.
All owned processes are closed and no guest queued. The closed portable copy was
hash-verified on E with its original path retained through a junction; no backing
chain moved. Physical0101/video0093, original0088 rollback, immutable0.1.0 and
peer work are unchanged. Full raw log, complete analysis, source capsules and
disk remain private, pinned by frontend.json and review001.json.

Next: close renderer/display admission and obtain actual worker-owned context
and per-object completion evidence while retaining this UI barrier. First capture
latest dirty data before any disposal. Do not turn a silent UI interval into a
native ownership grant or erase the remaining cache/reference evidence.
