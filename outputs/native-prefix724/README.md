# Native setup-prefix724: staged, not launched

This is the native-context counterpart of closed kernel-prefix723. It executes
11 common PRAMDAC writes and four CRTC writes (14,17,19,1b), stopping beforeCR22.
It uses the reviewed owned native bridge and validated720p framebuffer. It does
not program encoder/timings or attempt a full mode change or Windows boot.

The first mismatch stops forward writes. CR19 and680630 are restored when
attempted; sequencer/output and index selectors are restored. CR1b05 is retained
if attempted: this is explicitly NOT full pre-run state restoration. No attempt
to restore85, no retry, no CR22 data write or pending-bit clearing.

## Preparation and validation

- payload001 and host001 passed; fresh native payload4472bytes padded to9916;
  eleven absolute relocations;272byte RAM result.
- Twelve fresh diskless CPU fixtures passed and all VMs closed. They prove the
  exercised transition/refusal behavior, not physical GPU/cache semantics.
- integration001:54 modeled native/write/refusal cases; optical-review001:76
  whole-frame renderer cases. Native result values remain unobserved physically.
- build001 FAILED on accidental VIDEO_MODE_724P token. Original main.c and log
  retained. main002.c restores SDK flag and evidence label to720p.
- build002 FAILED parsing a duplicated assert; no build directory or process
  started. Failed script retained. build003 PASSED with exact tested payload.
- page-review002:30 cases; plan-review002:372 cases; host-plan001:131379 cases.
- linked-review001 confirms tested object nonrelocation instructions and exact
  bridge/payload bytes in both PE and XBE. source-review001 compares723/720.
- sources001 freezes sources, including failed attempts. Active launcher source
  main002.c; build003.py; physical controller physical002.py.

## Console state

Staged/read back only /E/Applications/XWNMode724/{owner.json,default.xbe}.
No startup hook, dashboard C access, ordinary launcher edits or Windows changes.
No launch requested. Console at UnleashX; awaiting watcher/reset availability.
XBE SHA256 dfa03591e925419f23f622201caab2a11e44f81a098ceda10077337f3663549a.

On launch it shows the initial blue picture, then native green handoff status
and second status bar (green724 success, orange returned rejection). It holds.
The13row photo is needed before power cycle. Preparation files cannot contain
post-handoff results; do not infer native readbacks from them.

Expected success rows, MSB left/white1/black0:
7240000d,00000004,00000005,00000724,0000000b,00000004,ffffffff,
ffffffff,ffffffff,00000001,00000051,00000005,000000fe.
See optical-schema001.json for each field. Preserve ambiguous photo bits.

Kernel723 success did not locate708/709 full-mode failure. A green724 result
would qualify only this prefix in native context, not CR22 or a full modeset.
Network/boot intermittency/1080i remain tabled. No GPU acceleration promotion.
