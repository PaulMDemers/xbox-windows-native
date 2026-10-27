# 742: bounded horizontal timing checkpoint

This is a distinct diagnostic after closed kernel740/native741 preservation
controls. It does not modify704, its full-byte checks, or any installed driver.
Reuse is source/evidence only; no closed runtime is reopened or parented.

The original phase5 in `../xcal-transaction704/transaction003.c` calls
`SetGPURegister`. Its retained `gpu_legacy.c` first writes these seven words,
before any additional CRTC, pitch or vertical programming:

| Offset | Field | Cromwell target | Required initial720p |
| --- | --- | ---: | ---: |
| 680820 | horizontal display end | 719 | 1279 |
| 680824 | horizontal total | 779 | 1649 |
| 680828 | horizontal CRTC | 719 | 1279 |
| 680834 | horizontal valid start | 0 | 0 |
| 68082c | horizontal sync start | 738 | 1389 |
| 680830 | horizontal sync end | 770 | 1429 |
| 680838 | horizontal valid end | 719 | 1279 |

Targets are evaluated from the retained720x480 Cromwell parameter structure,
not copied from kernel722's low-resolution register snapshot. The initial
values are admission checks against722's two retained720p captures; recovery
always uses742's own saved words. The named fields are also present in the
pinned envytools PRAMDAC description. Neither source establishes physical
write/readback behavior;742 tests that explicitly.

The existing preserving prefix is unchanged:11 MMIO and3 CRTC writes,15
full-value checks, no CR1b/CR22/CR33 data write. It temporarily changes CR19's
pitch bits, as740/741 did; the new horizontal portion adds no pitch write.
After all15 checks, write the seven timing words in original order, then read
them in order. On a mismatch retain its index, expected/actual values and the
untouched suffix sentinel. Restore all attempted horizontal writes in reverse
order and compare all seven full words with their own saved values.

No output-enable is sent unless those seven restoration comparisons pass.
If they fail, retain SEQ1=21 and gate5, restore the prefix's CR19 and680630,
restore selectors/CPU flags, save the result through the kernel and request
firmware reboot without drawing or waiting15seconds. No retry or guessed mask.
Prefix cleanup remains independently reported; a horizontal restoration failure
also leaves its SEQ1 cleanup bit set. A reboot request is not proof of recovery;
authenticated dashboard return and exact collected files are required.

Framebuffer admission checks the actual32-bit1280x720 allocation,5120-byte
pitch, scanout address, all900 physical pages and final byte against64MiB RAM.
The vertical extent, scanout base and pixel format are not programmed here.
Horizontal visible extent never exceeds the admitted1280 pixels; the prefix's
temporary1024-byte pitch is smaller than5120. Even with overlapping rows, the
conservative maximum fetched extent remains5120*719+5120=3686400 bytes within
the owned allocation. Output is blanked during the mixed configuration and
re-enabled only after horizontal recovery and the existing prefix recovery.
No additional framebuffer writes occur in the critical section.

No encoder, PLL, clock selection, PFB, interrupt/status clearing, vertical
timing, scanout-base, or additional CRTC geometry write is admitted. This is
not a visible480p switch, native execution, full mode replay or Windows test.
The700/704 legacy source and702 XML pins are checked by review_prepare.py.

Host checks execute the actual COFF with guarded memory and an explicit access
allowlist. They cover every forward read, every observable dropped timing
write, every restoration read, every observable dropped restoration, baseline
refusals, prefix failures, CPU/flags and selectors. HVALIDSTART is already0;
dropping its0 write is observationally indistinguishable, so that is not claimed
as a detectable fault. Linked code bytes and horizontal constant data are
checked in both PE and XBE. Models cannot prove physical timing or semantics.
