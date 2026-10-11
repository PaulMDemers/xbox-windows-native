# Power-policy caller identified; basic input remains responsive

The System reopens originate in the kernel's device-interface arrival callback
for power policy. Both captured failures reconstruct through
`IopNotifyDeviceClassChange -> MmDispatchWin32Callout -> IopPnPHydraCallback ->
PopNotifyPolicyDevice -> PopConnectToPolicyDevice(type=0) -> ZwOpenFile`.
The normal file-open path then reaches the keyboard/mouse class CREATE helper
and HIDCLASS's sharing denial. This is a power-policy connection attempt.

After both failures and debugger cleanup, emulated keyboard and mouse input
still responded: Ctrl+Esc opened the guest Start menu, Escape closed that menu,
and one relative mouse movement moved the guest pointer. The Found New Hardware
Wizard and Getting Started windows remained open. This establishes basic
response in this fixture, not complete input or power-button functionality.
No guest driver, policy, handle or setup-dialog change was made.

## Caller evidence

`caller-review002.json` bridges the actual saved syscall trap instead of
treating stack words as a call chain. The pinned NT5 PDB layout and exact
`KiSystemService` instructions identify the trap frame at F9037BB8. It saves
kernel CS=8, EIP=`ZwOpenFile+0xB` and EBP=F9037C90. Because this is a
same-privilege interrupt, the address of the HardwareEsp field is the original
kernel ESP; its contents are a return address, not a CPU-pushed ESP value.

That return is kernel RVA DDA18, immediately after `PopConnectToPolicyDevice`'s
call to `ZwOpenFile`. The six saved arguments exactly match the native service
arguments: desired access100003, sharing3, open options10, and stack-local
handle, object attributes and IOSB. Saved EBP, the callback's three register
pushes, and the Hydra callback argument bundle connect this to
`PopNotifyPolicyDevice`, with policy type0 and a valid interface-arrival event.
The notification's interface GUID is
`4d1e55b2-f16f-11cf-88cb-001111000030`; its Unicode name header is captured but
the name string itself is outside the captured stack.

The exact type0 success continuation builds a `PopSwitches` entry and selects
`PopSystemButtonHandler`. That continuation was not observed executing: the
open failed earlier. This identifies the intended system-button policy path;
it does not establish power-button/wake behavior or why this interface
registration was selected. The upper callback instructions are mapped from
the exact kernel image and captured stack, not individually live-breakpoint
pinned. Loaded kernel identity and the lower call sites were verified live.

`stack-review001.json` retains the lower frame observations, including FPO gaps
and a CSRSS trap-area word that is not a valid call frame. Nearest public symbols
alone are not interpreted as proof. The trap-aware review is authoritative for
the upper callback reconstruction.

## Sharing conflict and input check

`evidence-review001.json` independently reproduces hidreject007's finding:
System access100003/share3 conflicts with CSRSS access100001/share2. HIDCLASS
AD8 takes its deny-read branch to AF9/B03; completion, IRP and class helper all
return C0000043. At rejection, the existing HID contexts/files match the earlier
successful CSRSS opens and live B8/BC handles. No IoGetDeviceObjectPointer or
IoCheckShareAccess call is part of these failed class opens.

`input-review001.json` records the separately inspected native-window images,
image hashes and journaled commands. The owned xemu PID102884 was matched to
window148243502. Keyboard actions and the actual mouse movement used the
cooperative UI lease. The mouse guard rejected an attempt after the first
lease expired, before sending input; a fresh lease covered the actual movement.
The unused snapshot after that guard is not movement evidence.

The first HMP screenshot created no file. A second raw framebuffer capture was
unreadable under its linear interpretation. Both were capture-only attempts;
neither justifies a guest display/input failure. Native Computer Use capture
then showed the guest clearly. No setup dialog was dismissed or answered.

## Closure and validation

One corrected fresh fixture launched at2026-10-11T03:48:17.873309Z and was
host-closed at03:53:18.643715Z. Trace finished at03:49:23.755371Z with zero
remaining breakpoints and the guest resumed. All guest, observer, UI-lease and
cold-reader processes are closed. The immutable source remained exact.

Cold E/F allocation, protected files, five hives and log history pass. Target
resource installation, invalid-only HAL probes, lifecycle and cancel/remove
gates pass. QUERY_STOP1/CANCEL_STOP1/STOP0/START3; trace loads13/24/12 are
contiguous and below64. F contains319 directories and6726 files, with zero
allocation errors or orphan clusters. Guest payload hashes remain identical
to the established rebalance fixture.

One Kbdclass9/Mouclass9 pair and Ftdisk49 remain. DHCP1005 did not recur; earlier
failures are preserved. Pending setup258 still holds normal restart; there is
no Event6006 or dashboard-return qualification. Debugger and framebuffer
pauses exclude ordinary timing claims. No physical console was accessed.

The failed reopen008 observer is preserved separately: a host-side indentation
error caused NameError on the first unrelated kernel open. Cleanup and its
cold audit passed. A regression check reproduced that error and verified the
corrected dispatch before this fresh run. No used runtime disk was relaunched.

## Next boundary

Do not close CSRSS handles or weaken HID sharing checks. Basic input loss was
not observed, so this evidence does not justify an input-disruptive fix.
If pursuing the remaining event, inspect power-policy interface registration,
reannouncement and system-button capabilities with a fresh, focused diagnostic.
Power-button/wake, sustained input, functional network/SMBus, terminal takeover,
normal restart, repeated-boot persistence and physical qualification remain open.
