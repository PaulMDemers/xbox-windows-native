# Experimental open-source display surface cleanup

Candidate0097 is a new ReactOS framebuf.dll replacement, not a reconstruction
of the installed Microsoft display DLL. provenance.json identifies the baseline
as Microsoft5.00.2180.1. The source-level leak described here is not established
in that deployed baseline. An attempted baseline model used the wrong private
PDEV layout and was rejected; it produced no valid baseline regression result.

The pinned ReactOS DrvEnableSurface previously left its mapping allocated after
unsupported-format, bitmap-creation and surface-association failures.0097 unwinds
those paths, stores the mapping token separately from the visible framebuffer,
rejects a second enable while ownership remains, and deletes the engine surface
before unmapping. DisableSurface is idempotent after successful release.
DisablePDEV retries outstanding cleanup from a failed enable. If deletion or
unmap still fails, ownership is retained rather than freeing a live surface;
that error can retain resources until teardown/reboot and is not leak-free.

Fresh source tree a0a3f8b6bbd9c4fb60042554dd6d24130b0afddf was reconstructed and
compiled with pinned RosBE. Full display SHA256:
3d4c5c2659c06f9ae4c9a735a99ad972d4e773e02a0f1b7d4d8c2d18053e9db7.
Compiled execution tests inject every described failure and validate mapping
base versus visible base, call ordering, repeated disable, retry and rejection
of remap while release is pending. Imports resolve against the owned NT5 engine.
These modeled tests do not establish live concurrency or PnP stop/remove safety.

First fixture preparation refused the larger symbol-bearing DLL before writing
it. That unbooted child remains preserved. A strip attempt dropped nonpaged
section flags and was rejected without deployment. Fixture002 instead extends
only this file's allocation in a disposable child, verifies the exact FAT-entry
changes and cold-readbacks the original full build. No physical files changed.

The live experiment combines0096 miniport with this0097 display in the detached
startup protocol, fixed1024x576x32 mode and unchangedFATX0088. See launch/audit
reports for actual state. No hardware timing improvement or promotion is claimed.
Full miniport stop/remove/restart behavior and drawing-consumer quiescence remain
separate work; this patch fixes surface failure cleanup only.

The first ordinary boot completed all four GDI copy checks, all five timing
loops, payload verification, direct-RAM UC mapping and a normal shutdown. However,
the cold event audit found two rundll32 DLL-initialization popups while the window
station was shutting down. Therefore audit.json passed=false. It is not promoted
or ready for hardware. The detached launcher did not prevent the popups in this
configuration. No display-specific cause is established by this single run.
Owned emulator cleanup completed at2026-10-05T23:37:47UTC.

A later unchanged control from this same immutable fixture passed the strict
ordinary audit with no popups: ../video-installer-isolation/control003/audit.json.
That does not erase the first failure or establish a correction. It confirms
intermittency while qualifying that one bounded emulator run. No hardware
promotion or general PnP lifecycle claim follows from it.
