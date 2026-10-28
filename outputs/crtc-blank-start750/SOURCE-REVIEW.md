# Kernel CR02 checkpoint750

Closed748 source reused, no runtime reopened. Only next original CR02 write added
after qualified prefix/H7/CR04/CR05/CR00. Retained target720 implies(720/8)-1=89.
Actual749 preparation CR02=159, CR11=9; these are admission guards, not substitute
recovery values. Full CR02 and neighboring CR00/04/05 readbacks are required.
Restore own CR02 before CR00/05/04, then H7 and prefix recovery. Any timing recovery
mismatch inhibits output-enable and drawing; reports persist before restart.

133 words/532 bytes, retaining previous124 words. New words124..132 expose CR02
before/target/attempt/after/restored/mask, CR00/04/05 after CR02. Status75010 is
forward mismatch;75011 is CR02 recovery failure. Previous status precedence kept,
with CR02 recovery preceding CR00 recovery and selector mismatch last.

No CR03/later CR05/CR17/CR01, vertical/pitch/encoder/clock/scanout or CR1b/22/33
writes added. Kernel-only automatic return; no native handoff/Windows/visible
480p claim. Actual-instruction models establish contracts, not hardware semantics.
