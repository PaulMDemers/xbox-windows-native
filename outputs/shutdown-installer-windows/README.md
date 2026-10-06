# Read-only installer window inspection

A fresh child of the failed first-install idle fixture replaces only its idle
probe. The startup script, driver binaries, SYSTEM/SOFTWARE and video trace
remain as staged in the parent. Inherited manifest fields describe the earlier
parent edits; preserved_during_observer_staging describes this change.

The probe enumerates rundll32-owned top-level and child windows at five points
across120 seconds. It records class, control ID, parent, visibility, enabled
state and WM_GETTEXT contents. Each message has a100ms timeout; each sample is
bounded to256 controls/10 seconds. No activation, key input, button click,
window close, process termination or device setting change is used. Normal
restart follows the same two-minute interval, with observed duration recorded.
This guest observer can affect timing; it is not an ordinary stability run.

The original resource-model xemu executable is pinned to969a99a8, with that
experimental resource option unset. No host recorder, GDB or paused capture.
One launch per run ID, then cold logs/hashes/hives and full F: allocation audit.
Physical hardware is untouched. Any popup remains a strict failure.

References:
- [Microsoft WM_GETTEXT](https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-gettext)
- [Microsoft cross-process text and timeout discussion](https://learn.microsoft.com/en-us/archive/msdn-magazine/2001/august/c-q-a-getting-the-text-of-a-window-in-another-application%3B-making-backspace-work-in-the-explorer-bar)
- [Checking pending device installations](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/checking-for-in-progress-installations)

The owned NT5 cfgmgr32/setupapi binaries export CMP_WaitNoPendingInstallEvents.
That is an available completion-check candidate, not proof it returns the desired
state in this fixture. This observer does not call it or change shutdown policy.

## Result001: diagnosis obtained, strict FAIL

The probe completed120090ms and all five samples. At30/60/90/120 seconds,
GPU installation was already complete and the wizard explicitly requested
Finish. Its Finish button12325 was visible/enabled; Cancel was disabled. No
button was pressed. This identifies the outstanding UI, rather than an
unfinished GPU driver operation, during this particular wait.

A shutdown popup recurred. Windows logged one normal EventLog shutdown, but
never returned to dashboard within420 seconds. An unpaused framebuffer read
showed a blue background/cursor. After the timeout, a paused thread snapshot
reported no bugcheck, FATX resource-wait stack candidates and winlogon waiting
in PopFlushVolumes. Lock ownership/cycle was not captured, so a specific deadlock
is not proved. The existing decoder removed its raw memory. Owned host cleanup
then stopped the emulator. This is not a successful reboot or stability PASS.

All selected payload/runtime hashes and five structural hives pass. Full F:
allocation is consistent with zero orphans/errors. No other partition or full
binary archive is requalified. Sources, logs and snapshots remain retained.
The next diagnostic at ../shutdown-installer-completion finishes only the exact
successful GPU page once; it leaves unknown dialogs alone and records pending
installation status. It is a targeted setup experiment, not a driver fix.
