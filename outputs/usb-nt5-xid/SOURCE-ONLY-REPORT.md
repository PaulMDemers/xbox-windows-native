# NT5 XID transport and HID candidate

Original source now implements a WDM HID minidriver over the existing NT5 USB
stack. It validates the observed XID configuration and vendor descriptor, reads
one interrupt request at a time, and feeds the previously tested wire decoder
into a 13-byte HID gamepad report. Empty or malformed packets preserve the last
valid sample. Start requires a real sample before exposing input.

The report contains 14 buttons, four signed stick axes and two unsigned trigger
axes. This is a provisional mapping, not attended physical-control evidence.
The package and runtime ID guard currently accept only xemu's 045e:0202 device.

The USB request deadline cancels the IRP, then requires actual completion before
freeing or reusing memory. Stop/removal and queued device-power work join the
reader before releasing configuration. A lower driver that does not complete
cancellation can hold that wait indefinitely; the external emulator watchdog
is the diagnostic boundary. This candidate vetoes query-stop/remove while
started. It is not a general release-qualified removable-controller driver.

## Completed checks

- An independent short-item parser verifies the HID descriptor: one gamepad
  application collection, report ID 1, 96 payload bits plus the ID byte, exact
  button/axis usages and signed/unsigned logical ranges (`source-check.json`).
- All planned kernel, USB and HID entry points exist in the preserved NT5
  providers, including the actual Xbox HAL (`planned-api-review.json`). Actual
  linked imports remain a separate required gate.
- The immutable emulator seed still hashes to
  `7c09d05af676a7c37f242850837a8b2fa19b81a6ae63b2af2ec156e9a5fa197b`.
- Authored Python and PowerShell syntax checks pass. The repository exclusion
  check passed with the staged source; no compiled image or private disk is tracked.

## Pending execution

The shared build lease refused all 31 numbered attempts, including build031's
600-second bounded wait, which ended on 2026-10-10 at approximately 19:53 UTC.
The failures and individual queued refusals are retained in the build JSON
files. No build action acquired the lease; no compiler or owned emulator was
launched, and no USB build waiter remains active. **No compiled candidate, executed new C tests, guest installation,
NT5 HID input result, or physical deployment is claimed by this report.**

Prepared host tests exhaust the HID mapping's signed-axis word values and
pressure bytes, mutate the configuration/vendor descriptors, and compile the
actual USB wait/cancel function under nine deterministic fault schedules. They
are authored tests, not passing results until executed. The prior decoder's
66,083 checks and physical packet replay remain in `../usb-xid-capture/`.

The disposable guest harness stages only the new package, probe and startup in
its private overlay. It checks actual providers and full allocation before
launch, records exactly one launch intent, then checks installation and two
open/read/close cycles of 100 HID reports each. A normal restart is requested
only if the install queue is idle. A stalled run is host-stopped and retained;
cold collection separates functional input evidence from shutdown/persistence.
Idle cached HID reports do not count as independent USB transfers or deliberate
control-input coverage.

## Continuation

1. Complete a fresh unique `Build.ps1 -Attempt buildNNN -WaitSeconds 600` under
   the build lease; preserve compiler/test failures and correct them in a new
   attempt. `review-build.py buildNNN` must verify the actual linked imports,
   source snapshot and emulator-only package before launch.
2. `Run.ps1 -Case emuNNN` requires loopback credentials in the process environment,
   the exclusive emulator/UI leases, a fresh run ID, and at least 20 GiB on C:.
   Collect with the WSL `emulator-disk.py audit emuNNN` only after owned cleanup.
3. Inspect actual installation/read results, hive headers, protected providers,
   allocation and new event records. Retain any watchdog stop or pending wizard.
   Add lifecycle tests before a physical package/ticket.

The console has not been accessed in this work. The earlier native-capture
ticket remains closed; a future physical test needs a fresh serialized ticket,
fresh baseline capture and attended control labels. See DESIGN.md for the ABI,
ownership rules, limitations and primary references.
