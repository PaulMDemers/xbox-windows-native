# Resolved shutdown target: unfinished device installation

site-review.json pins the owned kernel's NtTerminateProcess instruction after
successful ObReferenceObjectByHandle. The target EPROCESS is at [ebp-8]. The
tracer can walk that process's page tables using QEMU's physical-memory read mode
without switching guest CR3. Nonresident parameters remain explicitly unknown.

Diagnostic run nt5-video-shutdown-resolved-001 launched at23:39:44UTC Oct5 and
returned to the dashboard at23:42:59UTC. It captured24 resolved termination
events. One CSRSS target was rundll32.exe running newdev.dll,DevInstall for
PCI\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1\2&ebb567f&0&28.
Its target command line was read using its own page tables, not the CSRSS address
space. See exit-trace.json. The final connection reset is owned emulator cleanup
after dashboard return, not a Windows crash; cleanup completed at23:42:59UTC.

device-install-review.json corroborates the exact command line and PID932 in
SetupAPI at23:40:24UTC. Driver selection returned0xe0000228: no compatible
drivers. Both retained SYSTEM hives identify the device as Multimedia Audio
Controller, with no Service or Driver value among the selected fields. It was
still alive when CSRSS terminated it during shutdown at23:42:37UTC.

Cold diagnostic checks passed: graphics, payloads, direct UC mapping, normal
restart and no new popups. ordinary_boot_qualified=false because breakpoint
pauses changed timing. This identifies a live unfinished installer, not the
source of the two popup events in other runs. No hard-error call was captured.
Next inspect the device-install queue and shutdown interaction in an ordinary
reproduction. Do not disable all PnP or waive popup checks to obtain a pass.
No physical access or promotion occurred.

[QEMU GDB physical-memory mode](https://www.qemu.org/docs/master/system/gdb.html#examining-physical-memory)
is used for bounded reads; the script restores normal GDB addressing afterward.
