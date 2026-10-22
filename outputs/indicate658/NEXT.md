# After658: qualify the indication path before another network attempt

Read REPORT.md, reconciliation001.json, audit001.json and closure001.json.
Physical658 is CLOSED: one accepted SITE, user saw only amber then dashboard,
zero UDP datagrams, 28 selected files unchanged and five hives parse. No complete
LED code or native status was recovered. Dashboard availability was bounded by
collection start at36.06seconds, shorter than the intended54-second indication
sequence. This does not distinguish early exit from indication/timer failure. Receiver/controller exited; persistent
Xbox-only UDP50657 rule remains installed and verified. No hook or Windows run.
Never rerun/recollect658, reuse its identity or restart its receiver directory.

Next design a fresh bounded indication control that separates reaching the
exporter from failure of the SMC/timer indication itself, without relying on
network success. First independently validate its actual linked entry path,
bounded waits, port access and reset/hold behavior. Existing host tests model
hardware callbacks and cannot establish actual LED timing or bus completion.
Retain original display capture boundaries and identify any added timing effects.
Do not silently insert instrumentation before capture and call it equivalent.

No specific cause is established. Static port comparison found no obvious
address mismatch, but does not qualify timer progress or physical transactions.
Do not weaken native admission, alter mappings/interrupts/cache settings, or patch
the functional display/NIC driver from missing packets or missing LED observations.
An independent external inbound network control is also still missing; verified
firewall policy alone does not prove delivery. Keep it separate from native sender
qualification, with fresh identity, bounded capture and source/binary pins.

Prepare and review the next candidate before any launch. One 20-second-bounded
SITE per admitted attempt; preserve uncertainty without retry. Existing user
authorization permits routine launches. Ask for a watched observation only for
a meaningful new indication, then collect once and audit retained bytes.

Ordinary720p/startup/savedXBOX480, releases and recovery remain protected. Dashboard
C is off limits. Physical lease retained, build lease free, automation paused.
Historical Ftdisk49/Popup26 remain unresolved. No full FATX, Windows restart,
NIC/DMA/cache/timer or GPU qualification is claimed.
