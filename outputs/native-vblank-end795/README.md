# Native CR16 vertical blank end — Test795

Fresh source-only derivative of closed native793 and kernel794. Adds the next
operation from pinned704: CR16 receives (saved & 80) | (524 & 7F), expected
ED -> 8C -> ED. Eight adjacent CRTC bytes are checked. CR16 restores before CR06,
the second CR07, CR10 and earlier CR07 operations. Final success requires all25
recovery masks clear; failed recovery inhibits output. No later mode operation.

The 20952-byte native payload is padded to21504 in an owned32768-byte allocation.
Offsets (hex): payload1000..6400; request6400..643C; request guard643C..6440;
result6440..6D50 (580words/2320bytes); result guard6D50..7000 (688bytes);
IDT7000..7800; stack7800..8000 (2048bytes). The independent memory review must
verify each boundary, all256 IDT entries, relocation and page checksums.

The first host construction succeeded, but integration006 rejected an out-of-bounds
timer scratch write at1EF0950 before completing its first case. prepare.py applied
an overbroad 8D8 ->950 substitution: the new request/result zero length was correct,
but two unrelated bridge timer operands were changed too. qualification-failure001
retains that failure, host003, host-plan002, lineage001 and cpu-build002. The twelve
CPU002 fixtures were built but never run; do not run them. bridge002.S restores
only those two operands to8D8. Fresh host004/CPU003/integration007 qualify it.
No hardware stage or launch occurred with the failed bridge.

Active build inputs main004.c/layout004.c are copied as main.c/layout.c by
build009.py. Do not directly make this kit. Use the existing build/emulator leases
and fresh output directories. Completed receipts are never overwritten or rerun.
Preparation sequence: payload_build005.py; host_build006.py; cpu003.py build;
model.py; integration009.py; optical_review003.py; cpu003.py run;
link_review009.py; build009.py; page_review006.py; page_boundary007.py;
plan_review003.py; linked_review005.py; source_review002.py; review_prepare004.py.
The unchanged native payload's734-case direct model is reused from this same
candidate qualification, not rerun after the bridge-only repair.

physical007.py uses private connection configuration, unique E paths, exact
readback and one SITE request with a20-second reply bound. No retry of an accepted
or uncertain launch. No startup hook, dashboard C access, ordinary launcher or
protected720p change. Native execution deliberately holds for a photo/power-cycle.
Files persisted before handoff are preparation evidence, not native disk results.

The optical report has thirteen32-bit rows, white1/black0, MSB left on gray:
signature, final status, eight recovery masks, then CR16 before/after/restored.
Seventeen masks are aggregate-only through final status; neighbor/CPU/selector
values are not displayed raw. Model results are not physical cache/timing/output
proof, full mode switching, Windows1.6 desktop support or acceleration evidence.

Standing user workflow: after taking a legible photo, the user power-cycles to
UnleashX without a separate Ready reply. Independently authenticate dashboard
before one collection. Ask for recovery only if it remains unavailable. This
workflow is not evidence of a normal Windows shutdown. See NEXT.md for live state.

Qualification completed:734 direct,724 full-bridge,76 optical,12 closed CPU,131379 host ownership,32+33 compiled page and372 compiled allocation cases pass. Exact frozen review001/sources001 and linked bytes pass. Physical outcome pending.
XBE SHA256 1425e9662c58a6b1505549e3709b51370e3f742d3a41d3cb507cf325b9521209.
