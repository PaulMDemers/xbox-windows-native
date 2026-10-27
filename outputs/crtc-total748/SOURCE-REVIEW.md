# CR00 horizontal-total checkpoint748

Next original SetGPURegister access after closed746/747 CR05 evidence is
CR00=(nvhtotal/8)-5. Retained target779 yields92(5c). Retained747 preparation
captures CR00c8 and CR11=09, whose write-protect bit7 is clear. These are
admission guards, not recovery data. Save this attempt's own byte for recovery.

Require full preceding prefix/H7/CR04/CR05 checks before writing CR00. Compare
its full byte and verify CR04=5d,CR05=3e remain intact. No masking or retry.
Restore own CR00 first, then CR05/CR04, check allthree bytes, then restore H7
and prior prefix state. A CR00 recovery mismatch prevents output-enable and
causes immediate durable checkpoint/restart without drawing. All earlier
CRTC/H7 restoration gates and prefix/selector checks remain in force.

The temporary mixed horizontal state stays blank. Owned framebuffer extent
remains5120*720=3686400bytes; no pitch, scanout, vertical, encoder or clock
change. No CR1b/22/33 data write. This is not a complete mode switch or native
or Windows test.124words496bytes preserve0..115 and append eight CR00 fields.

113actual-COFF cases include104 inherited and9new: baseline refusal, bad CR00
read/droppedwrite/badrecoveryread/droppedrestore, CR04/05 after-read faults,
and modeled coupling into each neighbor. New restoration faults inhibit
output-enable. Exact linked code, source delta and independent result schema
must pass before fresh hardware launch. Host evidence cannot prove GPU timing.
