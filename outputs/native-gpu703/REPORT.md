# 703 CLOSED: kernel480p survives the native handoff

The user observed green and supplied a photo. Native clock, output-control and
five CRTC-byte observations match the collected pre-transfer kernel records.
The640x480 framebuffer has2560-byte pitch,32-bit format and noninterlaced CR39ff.
This qualifies retention of this kernel-prepared display through this diagnostic
handoff, not native Xcalibur initialization or Windows support.

One SITE request was accepted at2026-10-27T03:49:42.966442Z. After photo capture,
the user manually power-cycled and confirmed the dashboard. Eight preparation
records were each read twice; source/binary/private-file/stage hashes and
unrelated E-root/Applications entries passed. No hook, Windows launch or normal
Windows restart. Runtime703 is closed; never relaunch/recollect it.

## Native optical results

| Row | Meaning | Value |
| --- | --- | --- |
| 1 | GPU PCI ID |02a010de|
| 2 | PCI command/status |02b00007|
| 3 | BAR0 |fd000000|
| 4 | CRTC25 |00000010|
| 5 | VPLL coefficient |0003c20d|
| 6 | Clock selection |100a0400|
| 7 | Output control |21101101|
| 8 | Packed CRTC39/28/19/13 |ff833a40|
| 9 | Framebuffer start |03eb4000|
| 10 | PFB configuration |Partial: known bits03070003, maskffff7fff; bit15 unknown|

The photo is private, SHA256
`bef4492ac1f56714a2185770274345c6bd9698f8983c23b6c6c979bc85f0a0ce`.
`photo003.json` checks319 bits across three thresholds and five offsets. All256
middle-row bits also pass independent adjacent-row geometry sampling. Colored
glare obscures row10 bit15; neither a previous capture nor the kernel value was
used to fill it in. Its31 known bits match the kernel PFB observation.

`photo001.json` preserves failure to isolate the first16 cells in the last row;
glare merged two white cells. `photo002.json` uses14 isolated calibration cells
and preserves the later ambiguous colored sample. `photo-review001.json`
preserves its incomplete-input IndexError. The final decoder records the
unknown explicitly; `photo-review002.json` passes. No full PFB value is claimed.

## Comparison and scope

Four complete shared MMIO values and all five CRTC bytes match the pre-transfer
kernel snapshot. Framebuffer03eb4000 matches the checked allocation and scanout:
1,228,800 bytes,300 page checks plus the last byte, no reserved-range overlap.
Stride includes the CRTC25 extension. PCI values are native-only observations.
The kernel snapshot and native capture are different instants, not atomic reads.
Saved CPU context is pre-file-write; final CPU shadow remained in RAM only.

Compared with closed720p701, VPLL0003c20d and selection100a0400 are unchanged.
Output control changes from21101100 to21101101. This is an observation, not a
new programming recipe or proof of that bit's meaning. Both modes retain their
kernel setup through native entry; pixel frequency and external routing were
not independently measured. The kernel640x480 timing differs from the pinned
Cromwell720x480 recipe; do not mix their widths, sync parameters or tables.

## Construction and checks

The703 source changes from701 are namespace,640x480 extent/drawing, CR25 capture
and stride validation, and rejection unless kernel CR39 isff. The CPU transition
is unchanged except the framebuffer extent and namespace. The new native page
is1027 bytes before tables at1216. Indexed CRTC and CF8 selectors are restored;
no CRTC data, native GPU configuration, encoder, clock, timer or interrupt-status
writes occur. Kernel mode setup itself is not read-only and its API is not
independently bounded, so this was a watched/manual-reset test.

Fresh tests passed18 linked register/pixel cases,10 full CPU fixtures,9 page,
19 allocation-policy and22 framebuffer-layout/pixel cases. All owned VMs and
host processes are closed. Build/emulator leases are released; hardware ticket
retained. Public records contain no proprietary binaries, photo or credentials.
Stage remains owned at E:/Applications/XWNNative703; ordinary launcher untouched.

Read NEXT.md. Native mode programming is still the next milestone.
