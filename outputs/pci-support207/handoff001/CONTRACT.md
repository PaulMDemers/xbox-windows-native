# Native NT5 HAL shared SMBus owner

This is an experimental free, single-processor Xbox HAL change. The physical
console remains on its restored baseline. Functional telemetry stays disabled.

XwnSmbusReadV1(Address, Command, Reply) is a kernel-only, versioned stdcall ABI.
Reply points to four writable nonpaged ULONGs: result, final status, poll count,
and byte value. The NTSTATUS reports ABI validity; the first ULONG reports the
transaction outcome. The result enum is defined in broker.h. It is not the old
driver004 reply ABI. Caller threads must be at PASSIVE/APC level and must retain
their device/remove/power ownership across the call. Interrupt/NMI callers are
outside the contract; an IRQL check alone cannot identify an NMI context.

The HAL retains one shared owner for its entire loaded lifetime. Atomic claim
is nonblocking. A second client receives BUSY; quarantined or terminal ownership
returns CLOSED. Only SMC AV-pack and ADM1032 temperature reads are permitted.
An initially busy external transaction is left untouched. A completion timeout
quarantines the owner until a new machine boot; a driver's stop/start or unload
does not reset it. There is no public slave-write or quarantine-reset operation.

HalpXboxPowerAction disables interrupts before exchanging the owner to TERMINAL.
On the supported single CPU, an interrupted normal client cannot execute again.
The terminal wrapper never restores interrupts or returns, including failure.
This is what makes takeover independent of a lock held by the interrupted code.
It would be insufficient on multiple processors; the integration rejects SMP
build macros and inherits the existing free UP HAL target.

Terminal entry waits for both busy flags to clear, with at most 10,000 polls and
10-microsecond stalls. It then sends at most one SMC power command and waits at
most another 10,000 polls. Error bits take precedence over completion. Reentrant
terminal entry issues no command. Failure is retained in the volatile HAL result
and the CPU halts. No abort/recovery strobe is assumed physically safe.

These are finite software poll bounds, not a measured wall-clock deadline or a
guarantee that a stuck controller can reboot the machine. The normal shutdown
driver gate must still drain its in-flight request. All future runtime clients
must use this HAL broker; an old direct-I/O client defeats shared ownership.
The assigned C000 range must remain pinned before PCI allocation. C200 retains
its observed firmware allocation without a guessed purpose.

The compiled model injects a noreturn terminal takeover at each callback boundary
using longjmp. That tests the actual core under the stated UP contract; it does
not simulate an SMP memory model, physically validate the controller, or prove
every instruction-level interrupt state of the linked HAL. Full HAL boot,
power/restart, stuck-controller model and physical qualification remain separate.
