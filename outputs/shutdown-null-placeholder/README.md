# Explicit unused-device configuration for xemu's PCI test function

The installed GPU can finish normally, but cancelling the unsupported emulator
placeholder wizard is temporary: completion004 cleared the queue once, while
subsequent boot006 encountered the same1B36:0005 installer and correctly withheld
restart. The held shell and process identity were captured after timeout; there
was no guest normal restart. Those failures remain preserved.

This experiment adds an original, narrowly matched null-driver INF. It matches
only PCI\VEN_1B36&DEV_0005&SUBSYS_00000000&REV_00, installs no binary, associates
no function service, and declares this unused synthetic function in System class.
The device remains enumerated. It does not implement the missing Xbox memory
controller model or the QEMU test protocol, remove the device, change its IDs,
set FAILEDINSTALL, suppress event errors, or modify the physical console.

[Microsoft's null-driver guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/installing-a-null-driver)
describes this configuration for unused devices without a function driver. Owned
Windows2000 display.inf/usb.inf also use empty AddService with flag2. See the
owned-file hashes and research in ../shutdown-installer-completion/research.json.
This is an explicit emulator compatibility policy, not a Windows synchronization
patch or proof that the original shutdown race no longer exists.

Case001 starts from the normally shut down completed004 disk, not a forcibly
terminated held run. It adds xwninf99/xwntest.inf to the already configured search
directory and replaces only the idle helper with read-only window/queue samples.
No offline registry mutation, dialog action or driver binary replacement occurs.
It writes fresh null.log/null-windows.log and refuses restart if installation is
pending after120 seconds. The original969a99a8 emulator has no host recorder or
resource-model option. Timeout snapshots, if needed, occur only after the return
deadline and remain explicitly diagnostic.

Qualification requires exact installed null INF/binding, retained enumerated
identity, no associated function service, unchanged real driver binaries, idle
installation queue, normal shutdown/dashboard return, clean new event deltas,
selected cold hashes/hives and full F allocation. An ordinary subsequent boot
without window sampling and the original mapping/BMP workload are further gates.
Physical popup ownership, Srv warnings and driver/hardware qualification remain
separate. No release/recovery baseline is replaced by this experiment.

The parent fixture already carries FAILEDINSTALL0x40 on01B0 and01B4 from the
earlier isolation experiment. Those inherited flags are not added or removed by
this kit. `003/device-inventory.json` records them explicitly. Consequently this
is a qualified sequence in that experimental emulator configuration, not a
clean full-device installation or a package eligible to copy onto the console.
The physical snapshot has neither of those failed-install flags.

## Initial package result001

The specifically matched INF installed through normal NT5 SetupAPI. An installer
was visible at the initial sample; it was gone and pending status was0 at30/60/90/
120 seconds. No dialog action was taken. The exact INF became oem3.inf, with
Xemu.Null binding, System class, ConfigFlags0 and no Service. Hardware IDs remain
unchanged. Normal restart/dashboard return, event delta, selected cold hashes,
five hives and full F allocation pass. Unsigned-INF diagnostics remain in the
SetupAPI transcript; no event record was suppressed. This is configuration
qualification for an unused synthetic function, not a function-driver test.

## Ordinary subsequent boot002

A minimal helper waits120 seconds and checks for pending installation immediately
before requesting normal restart. It does not inspect windows or click controls.
The queue is idle; SetupAPI has no new lines. Dashboard return, clean event delta,
unchanged selected binaries, five structural hives and full F allocation pass.
This case retains installed state from001 and does not reset the diagnostic trace.

## Original workload003

Prepared from the normally shut down001 state after002 passed. Only the startup
script changes to the exact original rehearsal command. Original probe/matched
binaries and BMP source remain identical. It requires527 mapping checks,16 BMP
API cases,50 exact files,34 absent intermediates and15 timed rounds totaling at
least60 seconds. This is not the fifteen-minute physical soak. There is no UI
helper, recorder or debugger. Launch and cold audit records determine its result.

003 returned normally at23:06:02UTC and passed the complete short workload,
event delta, unchanged selected binaries, five structural hives and full F
allocation with no orphan clusters or errors. No new SetupAPI activity occurred.
The original shutdown failure remains preserved; no claim of a kernel fix.
