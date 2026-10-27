#704 host work closed; next larger native bridge

Read REPORT.md, SOURCE-REVIEW.md, review003.json and closure001.json. Never rerun
or parent the closed704 host attempts or any closed703/701/700 runtime. Retained
source, blobs and receipts may be verified/copied as inputs to a NEW kit.

Authoritative candidate: transaction003.c plus encoder.c, exact gpu_legacy.c,
xcal_bus.c and headers. build004 raw9916-byte blob equals build003. Keep all
superseded sources/builds and cpu001/review001/review002 failures. Final host
coverage:880 transaction cases,32770 boundaries,12 relocated cases,9 rejections.

Next prepare a NEW native bridge/owned-page package. The old4KiB checkpoint is
too small. Proposed32KiB layout: first4KiB entry/GDT/IDT, transaction at+1000
(<=16KiB), request/result at+5000, separate stack+6000..8000. This is a design,
not an admitted allocation. Check the complete allocation and every low virtual
alias page; account for noncontiguous alias backing and every overlap. Check
all49 ELF relocations against frozen bytes, rebase only26 internal absolute32
sites, verify both physical and alias copies. Validate relocation, guards and
actual pre/post paging transition in fresh diskless CPU fixtures; do not claim
Unicorn port models are physical evidence. No kernel call after native entry.

Kernel preparation must use1280x720/3686400-byte owned buffer, not703's smaller
640x480 allocation. Capture CR11,CR21,CR44,sequencer and preserved CRTC fields in
the preparation report. Native entry must qualify PCI/controller bases, PM clock,
CPU context and ownership before calling transaction. Require CR11 bit7 clear,
CR21 maskfa,CR44zero, no doublescan. If these are absent, refuse and retain exact
evidence; do not silently unlock CR11, change shadow routing or borrow firmware.

Use physical framebuffer address after paging off. Protect clocks/PFB/interrupt
state. Bridge must report a bounded status and HOLD after transaction failure;
do not call firmware/kernel or retry. Full native480p initialization and Windows
on1.6 remain unqualified until a complete watched pattern is collected.

Incoming1.6 last known at UnleashX after703 collection, HDMI. No console access
this turn, no hook, no XBE, no VM/process. Hardware ticket retained, build/xemu
leases released; automation paused. OriginalConexant720p remains protected.
Networking,1080i,boot intermittency,RCT and acceleration remain tabled.
