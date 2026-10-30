# Kernel814 CLOSED: baseline refusal before new writes

One accepted launch, seven reports collected once, authenticated automatic dashboard
return. Actual CR1A=38 and CR2D=E0 differed from strict assumed00/00 baseline.
New four-control writes were refused (attempts0, forward/code81450, mismatch09).
Prior qualified prefix restored; audit002 PASS for refusal/integrity, experiment
not passed. Audit001 success-schema rejection and prefix001 host-checker failure
are preserved. No hook, Windows launch, normal Windows shutdown or owned host VM.

Next: fresh kernel815 with measured baseline38/10/83/E0, unchanged pinned704
write targets04/10/83/(savedCR2D & E0), exact host qualification, then fresh
native counterpart if successful. CR2D high bits must be preserved. Source-only
reuse of CLOSED814 allowed with pins; never relaunch/recollect/runtime-parent it.
Combined native visible mode and Windows handoff remain unproved. Automation paused.

Host: 1014 prefix,146 tail,2353 layout,26 frontend,10 clock cases passed.
COFF linked bytes checked in executable. Host models are not physical proof.
Large prefix receipts are losslessly retained in receipt-storage001.json.
