# Native valid-end785 diagnostic

Source-only extension of closed native783 frontend and closed kernel784 probe.
Tests NVVVALIDEND at GPU offset0x680818: saved value719, target479, restoration719,
with eight neighbors checked in each phase. Recovery precedes sync-end,
sync-start, valid-start, CRTC, total and display-end recovery. No CRTC7/10 writes,
full-mode replay, Windows launch or acceleration claim. Kernel784 passed the
transaction; native785 requires its own optical hardware evidence.

Result:430 words/1720 bytes at page offsets0x5100..0x57b8. The32768-byte allocation
and ownership policy are unchanged. Payload reserve1000..4c00; guard4c00..5000;
request5000..503c; result5100..57b8; guard57b8..5800; owned IDT5800..6000;
stack6000..8000 with low guard at6000. All256 IDT entries and pointer are checked.

Initial namespace preparation failed before compiling or accessing any closed
runtime. Payload004 failed size admission:14744 bytes exceeded14080 by664.
Fresh payload005 has the identical native instruction bytes, padded to15360;
its expanded reserve is possible because the probe-owned IDT moved4800->5800.
The relocated bridge and page builders require fresh CPU/full-path/optical tests.
Both failures are preserved; historical prepare.py and resize_layout.py must not
be rerun against this attempt.

The13-row report shows signature, final code, eight cleanup masks, valid-end before,
after and restored. Twelve other masks are aggregate-only through final status;
neighbors, CPU state and selectors are not individually exposed in the photo.
Final success requires all20 masks clear. Same-value CR02 and valid-start writes
cannot prove write effects. Preparation files end at handoff_armed and do not
substitute for post-handoff evidence. Host models do not prove physical behavior.

Hardware scope: user-identified1.6 with HDMI; uniqueE/Applications/XWNMode785 and
E/xwn-mode785 reports only. No startup hook, dashboardC or ordinary launcher
changes. One bounded SITE request. This probe holds for a photo and requires
manual power-cycle before preparation collection. See NEXT.md for exact state.
Private binaries and photographs belong underC:/xwn785, outside public inputs.

The complete direct-model receipt exceeds the repository5MiB per-file limit.
model001.json.part01/part02 preserve every byte; restore_model.py checks/rejoins
them without executing a runtime. The original local receipt remains untouched.
