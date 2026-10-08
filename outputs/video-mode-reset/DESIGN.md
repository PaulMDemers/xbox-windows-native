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
