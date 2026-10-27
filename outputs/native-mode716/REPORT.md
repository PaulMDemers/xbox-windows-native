#716 CLOSED: GREEN changed-register/restoration checkpoint

User answered "Yeah, now it's Green, holding" to the black/return and second-bar
question. Green supports optical0x716; the affirmative visible-return report was
not separately elaborated. User confirmed Ready after explicit manual power-cycle.
Nine preparation files collected once/double-read and audited. PCI/CRTC/SEQ,
geometry and allocation words match both714 and715; all source/binary/report pins
and independent alias ownership checks pass. No hook or owned host process;
console at dashboard. See observation001, audit001 and closure001.

This proves neither the undocumented bit0 meaning nor that630 is harmless when
left at2 for the rest of704. Immediate restore is a different transaction. It
does not identify the708/709 cause, qualify full mode switching or Windows1.6.
Next inspect remaining common-setup differences CR1b85->05 and CR22fe->ff;
justify a minimal bounded change before fresh host and hardware tests.

## Test design and validation

715 captured actual register680630=3 in two native passes matching both kernel
passes. Of the11 common-setup PRAMDAC writes in704, only this target differs (2).
Retained Cromwell associates630 with Xcalibur YUV output; bit0 semantics remain
undocumented. This bounded diagnostic tests the difference, not a driver fix or
a claimed cause of the708/709 black screens. See source-review001.json.

Fresh714-derived sources retain kernel preparation, framebuffer ownership,
32KiB physical handoff, CR11 check and the previously observed blank/restore pair.
Native code admits630=3, requests2 once and reads the entire32-bit value; then
restores saved3 once and checks it, pitch5120 and CR11 before the bounded wait.
Output restoration also rechecks630. CR19 is not written in716. No geometry,
encoder, timing, clock or interrupt programming. GPU data writes are limited to630 and the inherited CR1f/SEQ1 requests;
indexed selectors are restored. The existing framebuffer bars report status.

Host qualification:131379 ownership cases; four ASan/UBSan pages;12 fresh CPU
contexts/refusals, all closed;184 relocated instruction/whole-framebuffer cases;
23 actual nxdk page and372 ownership cases. Models include unexpected630
baselines, dropped/coerced test and restore writes, pitch/CR11 side effects,
late register change, timer bounds, and output restoration failures. They prove
control flow and write scope, not physical register semantics or visible output.

Success0x716 yields the green SECOND bar after restoration. Orange denotes a
payload refusal/error; cyan is the pre-call checkpoint, not716 success. Black
cannot identify an exact failed instruction. The test holds and needs manual
reset after observation. No Windows startup hook or console C access.

One SITE accepted at 2026-10-27T06:50:30.635274+00:00. Exact staged readback passed.
Asked final SECOND bar color, visible black/return, hold/dashboard. Physical
result was subsequently observed and closed above; no repeat launch. All previous runtimes remain
closed. No framebuffer mode or Windows1.6 qualification is claimed.
