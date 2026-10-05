# Build, display and release handoff

## Reconstruction

Resolve the exact base revision and ordered patch manifest. Numeric sorting is
unsafe when cumulative replacements and rejected experiments coexist. Replay
into a fresh private checkout, verify the resulting Git tree, and build with
explicit flags/tool versions. Do not reset the working diagnostic source tree.
Separate source reproducibility, repeatable build execution, byte-identical
outputs and hardware qualification; each needs its own evidence.

Pin compiler, build tools and container digests; keep source/build paths
parameterized. Record real commands and per-target output hashes. Imported
Windows media, firmware, dashboard binaries and user profiles are local inputs,
not artifacts to copy into a public source release. Build and package commands
should not implicitly deploy or launch the console.

NT5 applications must target its available imports and PE subsystem version.
Check the actual target DLL exports. A modern compiler may introduce runtime
helpers even when source uses no CRT; inspect the linked binary.

## Display contracts

The loader, HAL, memory manager, boot-video and miniport must agree on framebuffer
physical address, reservation, cache attributes, stride, dimensions and format.
Audit aliases and reserved PFNs before changing caching or drawing hooks.
An experimental PCI BAR model that makes Windows enumerate a device is not
evidence of faithful NV2A emulation or a physical driver fix.

Qualify drawing probes before timing them: test DIB-to-DIB, upload/readback and
overlapping copies in both directions; log the first mismatching coordinate and
RGB values. Control occlusion and pending paint messages. Software fill/copy,
screen readback and GPU operations have different costs. Emulator timing cannot
establish physical drag performance.

New modes require the console revision, encoder/output cable or HDMI adapter,
firmware capabilities, memory budget and handoff. A 4 MiB reservation can hold
one 1280x720x32-bit image by size alone, but not 1920x1080x32-bit. Those arithmetic
facts do not validate mode switching; 1080i also requires correct field timing.
Retain a known visible recovery mode while investigating.

## Release and upstream

Freeze a qualified source tag and archive exact installed files separately from
rebuildable source. Verify archive entries, hashes and recovery instructions.
Label whether restoration was actually tested. Do not alter an existing release
tag to absorb later experiments.

Before public release, audit history as well as HEAD for binaries, secrets,
personal/machine data and provenance. Source licensing must follow individual
components; do not assign a blanket license to third-party code. A sanitized
export can preserve a private forensic history without publishing it.

Inventory emulator deltas by source revision, patch hash, reproducer, unpatched
control and hardware evidence. Separate likely device-model corrections from
guest workarounds and synthetic experiments. Recheck current upstream code,
existing issues/PRs and contribution rules before preparing submissions. Keep
each proposal focused and retain an explanation a human reviewer can defend.
