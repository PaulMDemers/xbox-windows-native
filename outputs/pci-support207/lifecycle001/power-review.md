# Power-path review

The frozen build001 is a resource-only PnP integration diagnostic. It retains
the earlier power path and cannot qualify power management. Telemetry is disabled.

The path calls PoStartNextPowerIrp before PoCallDriver, while its completion uses
shared extension fields power_previous/power_target. That does not establish the
claimed serialization through completion. A follow-up candidate must notify the
power manager only after completing this driver's state update, and must retain
remove ownership until all completion work is done. Put transition state in an
IRP-specific context so an overlapping request cannot overwrite it. Resource
allocation validation is independent of this repair.

The function driver also forwards system power IRPs without mapping them to a
requested device power state. Consequently, boot and restart alone cannot prove
D0/D3 transitions. Any D0/D3 test must record the real power request/completion
and failure status, rather than infer it from shutdown or a PnP stop/start.
Wake/sleep/hibernate policy remains unimplemented and unqualified.

Microsoft's NT5 guidance places the device power policy owner's successful
device SET_POWER/QUERY_POWER readiness notification in the completion routine:
[Calling PoStartNextPowerIrp from a Device Power Policy Owner](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/calling-postartnextpowerirp-from-a-device-power-policy-owner).
The API describes notification as readiness for another IRP:
[PoStartNextPowerIrp](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-postartnextpowerirp).

This is a source review finding, not an observed guest failure or proof of a
particular concurrent NT5 schedule. Preserve build001 and its run unmodified.
