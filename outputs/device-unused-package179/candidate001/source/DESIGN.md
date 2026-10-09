# Explicit unused-device setup in a disposable emulator fixture

178 proved the owned restart guard refuses shutdown while installers are pending.
177 attributed a token-close race to actual console logoff cleanup. Neither fixes
device setup. This new configuration intervention stages an original null-driver
INF for the exact observed 10DE:01B0, 10DE:01B4 and emulator-only 1B36:0005 hardware
IDs. Descriptions explicitly say unused/no function driver. No device is removed,
no function service or binary is installed, no FAILEDINSTALL flag is written, and
no existing driver, service, event or crash-dump setting is changed offline.
Audio/SMBus/test-function capability is NOT qualified by this experiment.

Microsoft documents empty install plus AddService=,2 for unused devices:
https://learn.microsoft.com/en-us/windows-hardware/drivers/install/installing-a-null-driver
The owned NT5 INF providers also use this syntax. Current public documentation
and ReactOS machine.inf are design leads, not proof of this NT5 runtime behavior.
The new INF is staged into the existing Windows INF search directory; ordinary
guest SetupAPI must perform the installation. There is no registry fabrication,
automatic wizard cancellation, forced restart, debugger or physical access.

Use a fresh child of the immutable162 candidate. Same112 display driver/v4 probe,
identical178 compiled guard and five sample helper, unchanged strict event gates.
The unique xwnup179 namespace and startup command identify this single attempt.
Guard refusal/host-bound closure remains a held test, never normal reboot PASS.
If successful, require exact INF/binding, unchanged identities, no associated
function service, queue idle at both guard reads, normal shutdown/dashboard,
complete allocation/hive/protected checks, and retain all warning/popup failures.

A later independent ordinary boot from the normally shut down resulting state,
with no device setup helper/action, is needed to show durable settled installation.
This emulator-only compatibility decision must not be copied to physical hardware
or advertised as functional audio/SMBus support or a Windows synchronization fix.
No absence-of-popup claim settles the separate intermittent popup producer.
