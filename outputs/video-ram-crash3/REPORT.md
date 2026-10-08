# RAM0109 to boot-video crash handoff passed the mapped-page diagnostic

Single crash001 CLOSED. Unchanged RAM0109 DLL
ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440,
SharedUC0106 miniport/bootvid, FATX0103/HAL0102/NVNet0104/ATAPI0105 and exact
existing crash helpers. No physical action, driver patch or settings change.

Real probe entry identified kernel823e0000 through two pinned IDT gates. The
trace recorded34events/59resident pins and the intended E058D103 cookie. One
live RAM ownership slot, its PDEV/primary/shadow fields, semaphore and active
state remained identical before/after. No watched DrvAssertMode, disable-PDEV,
disable-surface or XwnUpload entry occurred between bugcheck and dump return.
This is retained ownership during takeover, not display-surface destruction.

Physical snapshots independently match all7,572 mapped display-text bytes to
the relocated owned PE; the first4,096 text bytes remain unmapped before/after.
Raw PDE/PTE entries and exact mapped bytes are retained. XwnUpload/DrvAssertMode
entries are also live-pinned. Whole RAM-driver residency is explicitly NOT
qualified. The crash path executes bootvid instead: all5,672 resident bootvid
text bytes match, with actual VidResetDisplay, VidSolidColorFill and
VidDisplayString at IRQL31. Shared framebuffer FCED6000 maps03C00000 with the
same owner, Ready1 and References1. Exact final physical RGB pixels match the
captured crash screen; intended stop/cookie and dump-complete text are legible.

Actual paired NVNet shutdown and genuine successful dump return were observed.
Three runtime payloads totaling65,536bytes exactly match the cold high-LBA dump
at disk offset148440145920. Extended ATA39 commands cover LBAs289922160/8,
289922168/64 and289922232/56 sectors. All9post-command block writes stay in that
extent. The28-bit alias11001192448 is unchanged and receives no writes.

Full cold allocation:326directories,6761files,327directory clusters,0errors and
0orphans. Five structural hives,35protected files, helper/startup hashes,
inherited emulator-only device configuration and96MiB/1536-cluster pagefile
pass. Event history retained, no new warning/error/application events. Normal
shutdown0 is intentional for this crash, never an ordinary clean-run pass.
Crash disk SHA36a4a1b48fe440afb5819b2977393b6251d0860393d1938e7002accbad200df7.
Original disk is preserved; no recovery boot of this image has been attempted.

Earlier failures remain separate. video-ram-crash failed on an absent PE
relocation directory and was stopped before the helper's flush/trigger; its
12orphans/4WMI chain errors are preserved. video-ram-crash2 correctly reached
bugcheck but failed its complete-display-text residency requirement. Its separate
post-failure snapshot proved the first text page unmapped in18process directories;
the visible/cold dump was not enough to qualify the missing callback trace.
This new protocol explicitly measures mapped pages, rather than claiming those
failed full-residency conditions passed. No guest bytes changed between attempts.

Host pin tests cover fixed-image, relocated-image and inaccessible-header cases,
rejecting code mutations. Physical-page tests reject code corruption, a removed
required mapping and an invented mapping for the absent first page. Frozen
sources, unique closed run identities and unchanged parents are reconciled by
history-review.json. No speculative driver change or event/service suppression.

Limits: one debugger-observed desktop crash. No arbitrary crash timing,
provider-lock interruption, surface replacement, new resolution, physical
qualification, whole RAM-code residency or recovery of this particular disk.
Earlier128GiB recovery qualification and physical0101/video0093 remain separate.
