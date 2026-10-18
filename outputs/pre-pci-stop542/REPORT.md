# 542 prepared and staged: C-stack-preserving checkpoint before PCI

The original first C function creates a stack frame, copies four configuration
values, initializes the memory manager, and installs the IDT before calling PCI
initialization. The IDT function also programs the PICs and disables the APIC
using its original code. This diagnostic preserves that entire sequence and
intercepts the PCI call at026004f8 with a terminal marker.

Unlike the prior pre-C marker, this marker must preserve the active C frame.
Its five-byte MOVESP is replaced with NOPs. Successful indication restores saved
registers/flags, then deliberately halts. Maskf5 produces alternating red/amber.
The earlier wrapper amber remains. No PCI or Windows execution is intended.

Twelve integrated host cases pass for actual C/memcpy/heap/IDT/marker instructions
with explicit PIC/APIC/SMBus/TSC models. The two existing configuration branches
and enabled/disabled APIC inputs are covered, with missing-heap and backward-write
negatives. Heap contents and all256 gates match an independent source/map spec.
Success preserves the C frame, all saved GPRs, ESP and flags except terminal IF
clearing. ESP is027fdf84 at the checkpoint; the marker reaches027fdf2c at its deepest.
Forty marker,19 controller and6 stage/capture cases also pass:77 total. These
checks do not prove actual physical cache, interrupt, mapping or device behavior.

Source hashes bind BootResetAction, BootLibrary and BootInterrupts to the original
374 build tree. Static review decodes each executed interval and checks vector
symbols against the map. WSL lacks rg, so source discovery used grep after that
read-only search failed; tool-note001 retains the limitation. No candidate-build
or host-validation failure occurred.

Package001 freezes55 pins. Candidate542839 bytes has SHA256
fcdad678b7e3709692c2a22eed0593697868df31ab3b7bf674a98087e9b17252.
Undoing six exact spans, same-length namespace strings and section digest recovers
the never-executed490 build artifact exactly. Sizes, copy lengths, other code and
padding are unchanged; no closed runtime is reused.

Staging finished22:21:33UTC at unique owned E:/Applications/XWNBoot542a, with exact
readback. Only that directory, owner.json and default.xbe were written. Ordinary
720p/startup/launcher checks passed before and after. No hook or Xbox C access;
stage process closed. No launch has been sent. Watch/reset readiness is pending.

A matching observation would support reaching this boundary in this instrumented
run. It would not attest HLT/both marker statuses, explain earlier failures, or
establish ordinary-boot reliability. The automation remains paused; no Windows,
D3D, GPU, game or release qualification is claimed. See DESIGN.md and NEXT.md.

## Single watched launch sent

The user replied "Proceed" to the staged diagnostic awaiting watch/reset readiness.
Fresh before1 completed22:25:07UTC and all10 files match closed541after1. One SITE
request was accepted22:25:23UTC; the launch supervisor closed without timeout or
retry. Exact frontLED/screen observation is pending. No console outcome or
Windows execution is inferred. No second launch, startup hook or XboxC access.

## Expected pre-PCI indication observed

The user reports "Amber/red flashing with a black screen". This matches the
distinctive target indication and supports reaching the checkpoint before PCI
initialization in this instrumented run. It does not attest HLT/both marker
statuses, establish correct interrupt behavior or diagnose earlier boot failures.

Manual poweroff/on and dashboard confirmation were requested. Reset completion
and fresh readback remain pending. No additional launch is planned for542.
