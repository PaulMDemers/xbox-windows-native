#710: held checkpoint before native mode programming

708/709 remain CLOSED failures:709 showed BLUE kernel picture then BLACK.
Their nine preparation records matched, but did not identify a native failure
phase.710 isolates the same larger handoff, PCI admission and bounded PM timer.

The only bridge change replaces a six-byte LEA before the704 call with a jump
and padding to the existing SFENCE/WBINVD/HLT path. Every other bridge byte and
all earlier symbol offsets remain exact708. The unchanged704 payload is still
embedded/relocated to preserve layout, but never called. The nxdk launcher differs
from708 only in attempt namespace; inherited mode comments/title do not imply
transaction execution in710. No native encoder, ACPI control or GPU MMIO access.
Kernel preparation still selects the existing1280x720 mode before the handoff.

Fresh host evidence:131379 ownership cases, ASan/UBSan construction at four
placements,12 diskless CPU fixtures (all closed),40 post-transition instruction
models,45 compiled nxdk page-builder cases and372 compiled ownership cases pass.
The40 models independently check the whole framebuffer and guards, exact CF8
save/capture/restore sequence, no payload execution, no GPU MMIO mapping, no
other port writes, timer boundary/wrap/stall/backwards/jump cases and refusals.
These are host tests, not physical/cache/scanout or Windows1.6 qualification.

Expected optical result: initial BLUE kernel picture for five seconds, then
thin GREEN native-entry bar at rows8..39 and CYAN admission-complete bar at
rows48..79. Both are inside the existing720p framebuffer. Second-bar refusals:
RED GPU PCI, YELLOW SMBus PCI, MAGENTA LPC PCI, ORANGE framebuffer request,
WHITE timer. A green entry bar alone does not prove admission completion.
No transaction pattern or automatic native return is intended.

## Closed physical result

Stage readback was exact. One SITE launch was accepted at2026-10-27T05:31:00Z.
User reported: "Yes it's cyan, holding." The second cyan bar is only drawn after
native handoff, PCI admissions and bounded PM progress; the transaction call is
skipped by710. This confirms reaching that checkpoint on this run. The user did
not separately describe the top green bar. No mode change was attempted.

After confirmed manual power-cycle, nine preparation reports were double-read
and audited. Last file phase is handoff_armed, still a pre-transfer record. PCI,
CRTC, sequencer, geometry and allocation mappings exactly equal709. Independent
alias/disjoint-range checks pass; private source/binary/report pins and unrelated
directory entries are unchanged. Native result RAM was not collected: the cyan
checkpoint is user-observed evidence, separate from preparation-file evidence.

710 is CLOSED. No startup hook, Windows launch or console C access. Dashboard
reachable; no owned host child; build/xemu released, hardware ticket retained.
Manual reset is not normal Windows shutdown.708/709 failure location remains
unknown; a successful checkpoint does not rule out intermittency or identify a
specific transaction instruction. Next isolate baseline checks before blanking.
