# Platform notes at 0.1.0

The loader, HAL, NT kernel and drivers have different responsibilities. Early
progress screens marked intentional checkpoints, not necessarily crashes.
The physical sequence established HAL base initialization, RTC calibration,
clock setup, partition-hook registration, BIOS reservations, memory-manager
entry, removal of low mappings, descriptor accounting, page tables, nonpaged
pool, PFN records, free lists, system PTEs and process address space before boot
video and the desktop. Preserve the exact inputs behind a checkpoint rather
than inferring success from a later screenshot alone.

## Memory and hardware handoff

Loader descriptors must exclude the framebuffer, loaded images, page tables,
HAL/BIOS scratch and reserved regions from the free-page lists. Descriptor
consumption was reconciled explicitly to avoid double-counted allocations.
The screen path had to survive removal of the original low mappings. A boot
logo establishes a working boot-video path, not a working desktop display
driver, storage stack or user session.

PCI resource modeling differed between the original console and xemu. The
physical framebuffer PCI view and a corresponding isolated emulator resource
fixture helped investigate that difference; they are not interchangeable HALs.
The physical release pins its own HAL and the exact tested loader. Diagnostic
debugger edits used to reach later code are exploratory evidence, not a
reproducible boot configuration. Preserve ordinary unmodified runs separately.

## Display

The current miniport reads inherited geometry from NV2A, accepts one 32-bit
RGB mode and maps the reserved framebuffer. It does not program encoder timings
or accelerate drawing. The framebuffer display driver exposes an engine-managed
bitmap without BitBlt/CopyBits hooks. Slow window dragging is user-observed;
uncached framebuffer reads/writes and copy volume are investigation targets,
not yet measured root causes.

The miniport initially supplied zero physical dimensions. Paint divided by a
zero HORZSIZE value. Patch0075 supplies a 96-DPI fallback size in millimeters;
that is a logical estimate, not EDID or the actual monitor dimensions. Test
all advertised device capabilities, not just width/height and a visible cursor.

The working hardware driver retains trace/PnP wrapper configuration. Earlier
plain-driver B4 failures require isolation before removing those wrappers.
Do not assume the disk-backed trace is a continuous rendering trace or the
reason for slow dragging. See the [video plan](../video-next/PLAN.md).

## Input, network, audio and power

Physical keyboard and mouse work. The user reports ping succeeds in Windows;
that qualifies basic observed IP reachability only. Next record address/target,
loss, both directions if feasible, then checksum-verified TCP transfers under
application load. Audio has experimental emulator work but no equivalent
physical qualification in this release. Treat playback, capture, mixer behavior
and latency as separate capabilities.

Normal Windows restart and return to UnleashX have been observed repeatedly.
Electrical power-off is separate from the safe-to-turn-off screen and restart.
Don't label the former implemented merely because shutdown messages appear.

## Recovery and test discipline

The original Xbox disk also contains unrelated games and applications. The
project uses an ownership marker, exact paths, hash-pinned payloads and scoped
changes. The release contains no repartitioning or format step. F: was selected
using metadata/capacity evidence, not only the dashboard's reported free space.
Shadow-C is a potential mapping issue for dashboard configuration, not evidence
that Windows's F:-backed system files live in raw C:.

FTP launch acceptance is not proof that Windows booted. Dashboard FTP returning
is not proof of a successful workload. A fresh attempt marker, completed result,
normal stop, persisted payloads and independent audits establish different
parts of the result. Never blindly repeat an uncertain launch or reuse an old
PASS file. Log collection itself can fail or block on the subsystem under test.

The latest physical run is quiescent, with automatic test startup disabled.
Local recovery bundles preserve the installation and manual files. Future tests
must retain this baseline and use new report/run identities. No scheduled test
or automatic Windows launch is part of the 0.1.0 release.
