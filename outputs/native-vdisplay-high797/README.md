# Native CR07 display-end overflow — Test797

Fresh source-only derivative of closed native795 and kernel796. Adds the next
pinned704 operation: CR07 display-end overflow for 480 lines, expected 74 -> 36
-> 74. Eight adjacent CRTC bytes are checked before/after/undo. Saved-value undo
precedes CR16 and earlier recovery. Final success requires all26 recovery masks
clear; failed recovery inhibits output. No later mode operation or Windows boot.

The raw native payload is22200 bytes, padded to22272 within the same owned32768
byte allocation and eight aliases. Offsets(hex): payload1000..6700;
request6700..673C; request guard673C..6740; result6740..70C8 (610words/2440bytes);
result guard70C8..7100 (56bytes); IDT7100..7900 (all256 entries); stack7900..8000
(1792bytes). Independent page, actual CPU, complete bridge and executable checks
are required before stage; layout-revision001 describes the unrun revision.

Preserve qualification failures:
- payload005 rejected the22200-byte raw result against its22016-byte reserve.
  The complete rejected source snapshot is rejected-layout001. No XBE/launch.
- integration007 failed before completing its first case: two harness reads of
  the existing second-CR05 attempted flag used byte offset610 instead of580.
  prepare.py had globally expanded the result word count and caught unrelated
  byte offsets. integration010 corrects only those two reads in a fresh attempt
  integration008. The already built bridge/payload bytes are unchanged.

Active frontend main004.c/layout004.c is copied as main.c/layout.c by build010.
Do not directly make this kit. Use existing build/emulator leases and fresh paths.
Completed receipts are immutable; do not rerun closed fixtures or failed outputs.
Active preparation: payload_build006; host_build006 -> host004; cpu003 build/run;
model -> model001; integration010 -> integration008; optical_review003;
link_review010; build010 -> build002; page_review006; page_boundary007;
plan_review003; linked_review005; source_review003; review_prepare005.
Source generators/older scripts preserve provenance and are not active build steps.
model001.json is reconstructed exactly with restore_model.py from public chunks.

physical007 uses private configuration, unique E/Applications/XWNMode797, exact
readback and one SITE request with20second reply bound. Never retry an accepted
or uncertain launch. No startup hook, dashboardC access, ordinary launcher or
protected720p change. Native code deliberately holds for photo/power-cycle.
Persisted preparation records end before native execution and are not native disk
results. A held successful image is not a full mode switch or Windows desktop.

Optical report: thirteen32-bit rows, white1/black0, MSB left on gray: signature,
final status, eight recovery masks, then CR07 before/after/restored. Eighteen masks
are aggregate-only through final status; raw neighbor/CPU/selector values are
omitted. Same-value CR02/NVVVALIDSTART/CR07total dropped writes are indistinguishable.
Host models do not establish physical cache/timing or output correctness.

User standing Oct28local workflow: photograph legibly, power-cycle to UnleashX,
no separate Ready reply. Authenticate dashboard before one collection. Do not
assume a normal Windows shutdown. See NEXT.md for current process/launch state.
