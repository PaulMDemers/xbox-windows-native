# Identify setup, then request a bounded guest restart

Fresh sibling from the same closed no-XID first-boot parent. No closed attempt
is relaunched. Storage drivers, kernel, HAL, loader, firmware and instrumented
emulator remain pinned to the preceding transfer experiment.

The phase-two probe retains the original 2226-byte workload, setup idle gate,
last-moment install checks and ExitWindowsEx request. After payload readback it
runs the pinned read-only observer for five samples over 120 seconds, joins it
within 150 seconds, and requires exit zero. It then runs the unchanged wizard
helper in a fresh directory, joins within 150 seconds and requires exit zero.
The helper checks exact known device command lines, process creation identity,
window/control text and foreground/active state before each Cancel message.
It never dismisses an unknown dialog. The setup API must actually report idle
for five seconds and pass the final restart check; there is no gate waiver.

The prior cold SetupAPI log names VEN_10DE&DEV_01B0 with no compatible driver.
Prior first-boot evidence identified helper targets 1, 2, 5 and 6. Live observer
samples will preserve the current command, device metadata and complete child
control text before action. Cancellation acknowledges unsupported devices; it
does not install a driver or prove hardware support. No new device disabling.

One loopback launch, exclusive cooperative xemu/xemu-ui leases, 480-second host
watchdog, then HMP stop/quit with exact process exit status. A timeout/forced
kill remains failure evidence. Guest normal restart requires dashboard return,
probe markers and EventLog shutdown in addition to full independent cold checks.
Ftdisk errors remain strict failures. This is an assisted diagnostic restart;
ordinary unassisted reboot qualification remains false. Root phase237 has priority
for its already frozen three-run matrix; acquire no emulator lease until it closes.
