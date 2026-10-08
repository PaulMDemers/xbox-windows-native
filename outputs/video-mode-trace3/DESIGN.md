# Probe124: actual same-mode display reset

New ordinary emulator child, unchanged RAM0109 binary and shared UC contract.
Twenty-six real GDI cases and authored color cursor visibility/replacement checks
straddle one actual ChangeDisplaySettingsExA CDS_RESET between cases12 and13.
Bounded enumeration records actual modes; current1024x576x32 must exist. CDS_TEST
must succeed. No registry update, resolution change or direct DDI invocation.
The screen DC is released/reacquired; afterward geometry, driver identity,
cursor position and deterministic redrawing are checked. Existing DIB memory
DCs remain alive. Old scanout contents need not survive a mode change.

Passive XwnModeStage exports bracket the reset and post-reset state for a later
fresh debugger child. API success is not lifecycle coverage. Actual callback
entry/return observations and raw scanout checks are required separately before
claiming disable/re-enable or surface replacement. Driver counters are compared
only inside each drawing case, never across a potentially replaced PDEV.

Ordinary strict gates retain all26 exact cold references, full allocation audit,
five hives, protected hashes, normal shutdown/dashboard, unchanged pagefile and
configuration, and zero new warning/error/application events. No physical access,
device policy change, cache changes or boot-video/crash handoff qualification.

API reference: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-changedisplaysettingsexa
DDI reference: https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvassertmode


## Independent diagnostic child

Exact probe124 and RAM0109 hashes are shared with the ordinary kit. Passive
markers bracket only CDS_RESET, after CDS_TEST, so enumeration/testing callbacks
cannot be misattributed to the reset. Nine lifecycle/registry helper entries are
resident-pinned and paired with returns using thread and actual stack cleanup.
First28 PDEV bytes (seven32-bit handles/pointers/active flag from pinned header)
are recorded before/after while live; freed PDEVs are never dereferenced.
Foreign shared-return hits are bounded. Entry/return calls from any actual thread
are retained. Module base/size is checked throughout; relocation or incomplete
pairing fails rather than silently accepting a coverage gap. Module unload/reload
is not forced. DrvDisableDriver's registered XwnOwnershipDisable is observed.

104 raw framebuffer/reference captures straddle the reset, using the existing
independent color-cursor/background oracle. No framebuffer writes, register
patches, direct DDI calls or policy edits. All breakpoints are removed and guest
resumed even on failure. Full cold gates remain mandatory. A no-op reset may pass
ordinary drawing but cannot qualify lifecycle coverage.


The first mode observer closed incomplete before reset: the fourth cursor capture
was followed by a single-step stop with all ten recorded registers and owner
unchanged, then an identical phase1/0 marker was seen again. This fresh child
keeps the removed breakpoint absent and requires observed CPU/owner progress
before rearming. At most four real single-step requests, all journaled; no marker
deduplication, no register/code edits, no discarded failure. This addresses the
recorded no-progress condition, not an asserted xemu/GDB root cause.


## Cold-reference oracle variant

The second observer closed incomplete after three valid cursor captures. HMP
memsave for the first restored reference produced only57344/393216 bytes;
its response was not retained, so the underlying cause remains unresolved.
This third unique child retains104 raw physical framebuffer captures and actual
runtime marker arguments/pins, but defers ALL pixel comparison until cold audit.
Each capture is compared against that case's393216-byte saved reference, with
the runtime marker's FNV digest, strict probe source/reference immutability logs,
exact cold reference checks and independent RGB/cursor formulas. The probe itself
is unchanged. No partial virtual dump is substituted or called complete.
Live reference residency is not claimed. Cold reference persistence and104 exact
pixel outcomes are required. HMP physical capture responses are journaled.
This changes the reference acquisition method, not the expected pixels or cold
gates; both earlier failed diagnostic attempts remain failed and immutable.
