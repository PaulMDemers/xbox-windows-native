# 659: independent latch around the original timed indication

CLOSED: solid green on a held black screen, then manual recovery and passing
selected-file integrity audit. This diagnostic separates the original
658 timed LED routine from a timer-independent result latch. It freezes the
original display capture before any new indication, does not call the network
sender, never resets automatically, and deliberately holds for a user power-cycle.

The source-only input is closed658's pinned tree, not its runtime. New tree:
`e7fd7aa309878bf36a10ac3980751d659d251a3d`. XBE is315024bytes, SHA256
`e8698a90ecdf91c8d945fb3147aec1c3f65bbfd9879b7e0b500599e466505ed8`,
staged/read back at `/E/Applications/XWNControl659/default.xbe`.

## What runs

1. Unchanged capture/apply/post-capture caller enters the exporter; freeze and
   encode with a fresh private identity. Nothing is transmitted.
2. A new bounded polling-only SMC writer attempts an amber/off entry latch.
   It uses at most100000 reads per wait, no timer, no retry and no reset command.
3. The original linked `show658` runs its green/off four-second indication with
   the original two-second dark separator and unchanged `delay656`.
4. The polling-only writer attempts a persistent final status, then executes HLT.

| Final indication | Meaning if the final latch succeeded |
| --- | --- |
| Solid green | Entry latch and original timed indication reported success |
| Red/off | Original indication returned a delay error |
| Alternating red/green | Original indication returned busy timeout |
| Alternating red/amber | Original indication returned completion status error |
| Alternating green/amber | Original indication returned completion timeout |
| Amber/off | Original indication succeeded but entry latch failed |
| Solid red | Encode error or unexpected indication argument error |

If the final latch fails, the previous LED state can remain. In particular,
amber/off alone is ambiguous with the entry marker. No LED observation proves
raw status register values or all source stages. A dashboard return would be
unexpected for this control and cannot be called a normal restart. The user
confirmed availability to reset after reporting the light.

This changes post-capture timing and SMC traffic and removes networking/reset.
It is a control, not a fix to native timer, network, display or boot behavior.
No mapping/cache/interrupt state is changed or firmware state borrowed. Poll
counts are finite; a physical I/O bus stall is not recoverable by that bound.

## Validation and preparation

269 sanitizer cases cover masks, polling bounds, transaction failures and result
selection. Ten exact-linked executions cover normal/wrapped/frozen/backward
timers, original indication busy/status/completion errors, entry/final latch
failure and encoder rejection. Unlike658's earlier linked harness, these run
the actual `show658`, delay and SMC routines: only raw IN/OUT hardware responses
are modeled. Packet bytes are preserved; no network or reset instruction path
is entered. This is still not physical timing or indication qualification.

29 artifact review checks pass, including18 unchanged old object sections,
unchanged original indication and original display caller, dependencies and
freeze/entry/show/final/hold ordering. Build/compiler/source pins are retained.

Controller-review001 FAILED because its mock expected the wrong executable path;
no physical launch was sent. Preserve that failure. Fresh controller-review002
validates the corrected exact path and one-shot accepted/uncertain requests.
Use `physical_v2.py`, which also explicitly requires the review's passed flag.
V1 was used only for read-only preparation; it must not launch this candidate.
The v2 controller is hash-pinned by controller-review002. No gate was waived.

28 selected files were captured twice before staging. Ordinary720p/startup and
savedXBOX480 remain protected. No hook, UDP listener, VM or guest disk was created.
Persistent Xbox-only firewall remains installed. Physical lease retained, build
lease free, automation paused. Selected-file integrity is not a full FATX audit;
historical Ftdisk49/Popup26 remain unresolved.

## Physical result and limits

One launch was accepted2026-10-22T21:34:45.417269Z. The user reported solid green,
then explicitly confirmed the screen remained black. A bounded read-only probe
found the dashboard unavailable. This matches the control's successful entry
latch and original show658 return followed by final latch and intentional hold.
No raw BSS status record was recovered, and actual indication duration was not
measured. No network sender, reset request or Windows run was intended.

The user power-cycled as requested and confirmed the dashboard. One collection
completed21:36:50.961134Z: all28selectedfiles unchanged, five hives parse, saved
XBOX480 intact, event history unchanged, no new6006. Manual recovery is not normal
Windows shutdown. No hook or receiver existed; all owned host processes exited.
The persistent firewall was verified again and retained. See observation001,
recovery001, reconciliation001, audit001 and closure001. Never rerun/recollect659.

This is one observed control success, not a root cause for658. Extra entry/final
SMC transactions and removal of networking/reset are material differences.
Next use a persistent post-network result latch in a fresh, independently tested
attempt, retaining frozen data and safe/unsafe cleanup distinctions. Missing
packets alone must not relax native admission or cause a functional driver patch.
