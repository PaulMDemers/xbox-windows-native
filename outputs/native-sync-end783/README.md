# Native sync-end783 diagnostic

Source-only extension of closed native781 frontend and closed kernel782 probe.
Tests NVVSYNCEND at GPU offset0x680810: own saved value729, target492, restoration
to729, with eight neighbors checked in each phase. Recovery precedes sync-start,
valid-start, CRTC, total and display-end recovery. No0x680818 write, full-mode
replay, Windows launch or acceleration claim. Kernel782 already passed the same
transaction; native783 requires its own optical hardware evidence.

The result is400 words/1600 bytes at page offsets0x5100..0x5740. The request and
result reserve ends0x5740; guard continues to0x6000; stack occupies0x6000..0x8000.
Payload reserve remains0x1000..0x4700, then guard to0x4800 and IDT to0x5000.
No allocation boundary was expanded to fit the new code.

First-Os payload003 failed its size gate:14296 bytes exceeded14080 by216.
Fresh-Oz payload004 of identical C sources fits13688 bytes, leaving392 bytes
of deliberate0xcc padding. Reviewer006 failed because it assumed zero padding;
fresh reviewer007 checks the actual0xcc contract. Both failures are preserved.
Compiler optimization changes instructions: no binary equivalence is claimed.
Fresh direct, full-path, CPU and optical qualification is required.

The13-row report shows signature, final code, eight cleanup masks, sync-end before,
after and restored. Eleven other masks are aggregate-only through final status;
neighbors, CPU state and selectors are not individually exposed in the photo.
Same-value CR02 and valid-start writes cannot prove write effects. Preparation
files end at handoff_armed; they cannot substitute for post-handoff evidence.

Hardware scope: user-identified1.6 with HDMI; uniqueE/Applications/XWNMode783 and
E/xwn-mode783 report files only. No startup hook, dashboardC or ordinary launcher
changes. Exactly one bounded SITE request per admitted attempt. This probe holds
for a photo and requires manual power-cycle before preparation collection.

See NEXT.md for current stage. Private binaries and photos belong underC:/xwn783;
none are public repository inputs. All prior runtimes remain closed.

Staging-failure001 preserves an ignored link.ld caught by the exact staged-byte
check. Explicit manifest-only staging corrected it; all41 frozen source bytes
then matched. No hardware access occurred before this correction.
