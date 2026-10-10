# OS-generated resource-rebalance diagnostic

This disposable NT5 emulator attempt tests STOP and CANCEL_STOP on the exact
SMBus DEV_01B4 instance. It is a diagnostic intervention, not evidence that an
ordinary boot naturally rebalances this device. It performs no SMBus transactions.
The HAL ownership candidate remains unchanged.

The helper retains a handle to the matching device interface. A versioned
diagnostic IOCTL arms a one-shot state response and calls IoInvalidateDeviceState
on the PDO. The driver forwards QUERY_PNP_DEVICE_STATE, then combines the existing
result with PNP_DEVICE_FAILED and PNP_DEVICE_RESOURCE_REQUIREMENTS_CHANGED.
Microsoft documents this combination as requiring STOP before new resource
assignment. The original constrained resource policy remains in force; the helper
never constructs a PnP IRP.

Phase 0 allows Windows-generated QUERY_STOP, STOP and START. Phase 1 arms a
one-shot QUERY_STOP failure and expects Windows-generated CANCEL_STOP. Each phase
requires a successful query after recovery. The veto phase also requires unchanged
START and STOP counters. Polling is bounded to ten seconds per phase. Cleanup
withdraws both one-shot flags. Missing IRPs are a held result, not a pass.

The run then exercises the existing held-handle QUERY_REMOVE/CANCEL_REMOVE test,
safe removal, re-enumeration and property-change restart. Pending installation
blocks normal Windows restart. No unrelated setup dialog is dismissed.

Build 001 failed before guest preparation because three intentional switch
fallthroughs were not annotated under -Werror. Its source snapshot and pipeline
record are retained in failed-build001. Build 002 adds recognized fallthrough
comments without weakening compiler warnings. It uses fresh output and journal
paths. The prepared guest is launched at most once. All preparation, execution
and cold auditing use cooperative resource leases.

The final cold audit checks protected bytes, five registry hives, old log history
and complete E:/F: allocation ownership. Host-bound closure is recorded separately
from normal restart. A fresh first boot cannot qualify repeated-boot storage,
functional SMBus reads, terminal takeover or physical hardware.

Primary API references:

- [IoInvalidateDeviceState](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioinvalidatedevicestate)
- [Windows 2000 and later QUERY_STOP handling](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-an-irp-mn-query-stop-device-request--windows-2000-and-later-)
- [Stopping a device to rebalance resources](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/stopping-a-device-to-rebalance-resources)
- [PNP_DEVICE_STATE flag combinations](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-an-irp-mn-surprise-removal-request)
