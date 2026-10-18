# Entry/file boundary indicator prototype

Physical501 supplied no file. Emulator502 executed its exact early file gate and
completed six actual calls, but cannot identify the physical missing-file cause.
Earlier physical307 identifies kernel1.0.4034.1,623712-byte image,timestamp1004048809;
502 has size636160,timestamp1023192752. The expected API ordinals exist in both
retained export tables, at different addresses. This is historical physical
evidence, not a current firmware/loader identity capture or a diagnosed ABI defect.
307's private kernel formerly onD was not found in checked C/E locations; no
current private-kernel rehash or new disassembly is claimed.

Do not move470's raw SMBus/CLI marker into active early Xbox-kernel execution.
The new proposed outer gate calls the kernel's HalWriteSMBusValue ABI instead.
It writes amber pattern register8, enables manual mode register7 only on pattern
success, then requests a two-second relative nonalertable kernel-mode delay.
The original registers/EFLAGS are restored before jumping into byte-exact498.
Indicator failures remain recorded and do not suppress the independent file gate.

The exact498 source is included with only its firmware-symbol integration alias
changed; its completion target is a new entry-only return routine, not Windows.
After state7, the routine captures the restored register image, requests green,
holds two seconds only if green and earlier manual-mode calls succeeded, then
requests automatic LED control once and firmware return1. File failure routes
through the same automatic-mode cleanup, then returns. No retries, raw I/O,
CLI/STI, page/segment/control-register changes, allocation, video changes or
Windows preparation are in the proposed outer gate. Reentry makes no further
indicator/file requests and preserves the first metadata.

SMBus,delay and firmware implementations are NOT bounded by this prototype.
The call count is finite, but an individual kernel call can stall. A future
controller needs an outer observation bound and must report a console still
running rather than infer successful return. The terminal firmware call traps if
it unexpectedly returns. No host result proves actual LED visibility or return.

A visible amber phase would positively support entry through the initial API
calls; no amber remains ambiguous. Green is requested only after the file gate's
final flush/close returned successfully. A complete112-byte receipt still does
not prove those final calls by itself. Automatic-mode restoration can fail and
must remain visible in actual metadata, never silently treated as restored.

Host001 executes actual i386 assembly and original498 file gate. Every Xbox API
is an explicit model. It covers199 inherited file/register cases and94 indicator
failure combinations, including failures at every LED/delay position, DF set and
clear, partial files and failed cleanup. Repeat entry is exercised once per case.
No new XBE, emulator, physical stage or console launch occurs in503.
