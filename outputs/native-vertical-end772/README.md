# Native772: bounded vertical display-end checkpoint

This candidate follows the source-qualified kernel771 transaction: after the
existing horizontal/CRTC prefix, change only NVVDISPEND at GPU offset0x680800
from its observed719 to479, then restore its own719 before restoring CR13 and
the preceding operations. Read four vertical neighbors and CR13/CR19 at each
stage. Unknown offsets680808 and680814 remain unread. No NVVTOTAL, encoder,
PLL, framebuffer-base or complete mode-setting extension is admitted.

The source-only770 native frontend supplies the owned framebuffer, checked
allocation/alias mappings and bounded paging-off bridge. No closed runtime is
reopened. The772 probe matches771 except its namespace and native CPU contract.
Output recovery requires all14 masks clear. A green held pattern is a diagnostic
result, not a Windows1.6 boot, successful complete480p mode or acceleration claim.

## Memory contract

The first payload build stopped before staging:12664 raw bytes exceeded the
old9916-byte extent. Its receipt and private files are retained. Payload002 uses
12800 bytes: page offsets1000..4200. IDT4800..5000, request5000..503c,
result5100..5500, guard5500..6000 and stack6000..8000 remain disjoint. The
allocation is still32768 bytes. The13 absolute relocations remain independently
validated within the exact payload; bridge entry and page construction use the
new extent. Host COFF review keeps relocation input outside the larger payload.

## Qualification and operation

Use the repository build and emulator leases. Build payload with
payload_build002.py in WSL, test its actual ELF using model.py, construct fresh
pages using host_build005.py, build/run fresh diskless fixtures with cpu002.py,
then run integration004.py and optical_review002.py. source_review.py checks
source deltas, report offsets, faults and reservation boundaries. build005.py
embeds the exact qualified bytes; page_review003.py, plan_review003.py and
linked_review004.py check the compiled frontend and actual PE/XBE linkage.
review_prepare.py freezes inputs only after all required checks pass.

Stage the unique owned E application using physical003.py and private local
configuration, with exact readback. Native launch needs a current watcher who
can photograph the13-row report and power-cycle afterward. One SITE request,
20-second reply bound, no retry of an accepted/uncertain launch. There is no
startup hook. After manual reset, collect preparation files once/double-read,
decode and independently review the private photo, and audit_collection.py
checks the retained records locally. Manual reset is not normal Windows shutdown.

## Optical report

MSB at left, white1/black0 on gray. Rows: signature, final status, prefix,
horizontal, CRTC, CR00, CR02, CR01, CR13 and vertical recovery masks, followed
by NVVDISPEND before/after/restored. Six additional recovery masks are omitted
raw; final772 still requires every one of the14 masks clear. Neighbor values,
CPU state and selector readings are not individually visible in this report.
Expected triplet is719/479/719. Private photos and executables are not public.

See NEXT.md and actual receipts for current state; this document is procedure,
not evidence that any pending stage passed.
