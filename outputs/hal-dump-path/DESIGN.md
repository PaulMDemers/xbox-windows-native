# Fixed-root crash-dump path accounting

This isolated emulator candidate follows the pinned dispatch/completion evidence
in ../dump-usage-trace. The current HAL's paging-only selector inherits
STATUS_NOT_SUPPORTED for dump usage and completes it at the root PDO. No FATX
retrieval-pointer operation is reached. This change implements the root's own
obligations; it does not override any lower-driver or filesystem result.

The fixed Xbox root has no parent device or extra power relationship to notify.
Its PDO power branch completes requests without a hardware power-down operation,
and it does not register for idle detection. This remains true after the change.
The root stays powered; lower storage drivers retain their own power decisions.
PnP and power dispatch are checked in resident, nondiscardable .text in both
rebuilt HALs. Existing DO_POWER_PAGABLE clearing remains in the usage-success
path. No new pageable allocation, I/O dependency or dump-writing callback is
introduced in the root handler.

0102 adds separate paging and dump counters. A compare/exchange loop refuses
underflow, invalid negative state and signed overflow without publishing a
transient invalid count. Removing one usage type cannot remove another's
protection. Any nonzero counter keeps query-stop/query-remove busy and reports
PNP_DEVICE_NOT_DISABLEABLE. Hibernation and unknown types retain the unsupported
behavior. Successful usage updates invalidate device state. IoCreateDevice's
zeroed extension initializes both counters; its allocation uses sizeof of the
updated PDO_EXTENSION.

The production counter function is extracted into a host harness with atomic
shims: empty removal, negative state, MAXLONG addition/removal, independent
type counts and 400000 concurrent balanced pairs pass. These are counter tests,
not guest power or crash-dump qualification. The rebuilt control and candidate
share compiler pins, definitions and source series except0102. Both use serial
mode for the same 792-append/32-shrink/132-reopen/11-file regression. Only their
HAL differs; FATX0101/video0093 and inherited emulator device policies remain.
No configuration/service/event suppression is permitted.

This follows the [Microsoft usage-notification contract](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-device-usage-notification):
special-file lifetime tracking, resident dispatch, power retention and
stop/remove protection. Actual dump initialization may still fail later.
Cold files, allocation, hives, protected hashes, normal shutdown and strict
event deltas remain required. Real dump write and reboot recovery in a disposable
owned emulator child are necessary before claiming end-to-end crash-dump support.
This candidate is not a physical FATX corruption fix or hardware-qualified HAL.

The first build invocation (hal-dump-path-001) was blocked before creating its
output directory: C: had17620279296bytes free against the21474836480byte reserve.
The wrapper initially returned host status0 despite the nested Python failure;
the retry explicitly checks LASTEXITCODE. No candidate was produced by that
invocation. Four closed standalone kernel runs036/041/042/043 were copied and
hash-verified to E: with original paths retained through junctions. No backing
chain was relocated. See ../task-storage-offload/manifest-20261007.json. Candidate
build002 and matched control001 then passed the original unchanged space guard.
