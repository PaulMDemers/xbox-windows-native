# Live NT5 START resource diagnosis — closed

The instrumented resource-only driver again installed but reported Code10.
The retained trace identifies our own validator as the cause: FILTER succeeded
and pinned the xemu profile2 resource to C000–C01F, then the actual START_DEVICE
raw and translated lists arrived with version/revision0/0 and port flags0x31.
The previous validator accepted only the BootConfig encoding1/1 and0x01 and
returned STATUS_DEVICE_CONFIGURATION_ERROR before forwarding START.

The captured raw and translated lists are identical52-byte buffers. Trace SHA256:
1f9def3405f4786c6068d9176c701df3ea5e4ae39e7ec5c99dd51d9f08d7aeb0.
emulator001/resource-trace.json retains all bytes and the filter/start outcomes.
Flags0x31 combine I/O,16-bit decode and positive decode. The Microsoft structure
documentation specifies version/revision1; accepting0/0 is a compatibility rule
based on this pinned live NT5 observation, not a claim about the documented form.

Build004 is the first successful reviewed build. Three earlier failures are
preserved under failed-build001–003: unsupported ZwFlushBuffersFile declaration,
a helper warning, then actual-provider rejection of the unexported kernel API.
The final trace uses FILE_WRITE_THROUGH and user-mode FlushFileBuffers instead.

The power repair moves NT5 readiness until after completion updates. A reserved
transition context/work item avoids allocation inside SET_POWER. The diagnostic
IOCTL uses real PoRequestPowerIrp requests, with remove ownership retained through
completion; it does not directly call the dispatch routine. These paths were not
reached here because START failed. See the later lifecycle003 observation.

The fresh guest ran20:02:22–20:05:22UTC on2026-10-10, then closed at its180-second
host bound. Probe exit23; no normal restart or event6006. Do not relaunch.
Cold protected files, five hives, prior logs and allocation passed
(319directories,6726files,320directory clusters, no errors/orphans).
The full binding delta is retained; Ftdisk49 and global setup remain unresolved.
No telemetry, HAL replacement or physical-console access occurred.

References: [CM_PARTIAL_RESOURCE_LIST](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_cm_partial_resource_list),
[CM_PARTIAL_RESOURCE_DESCRIPTOR](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_cm_partial_resource_descriptor),
[PoStartNextPowerIrp](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-postartnextpowerirp),
[PoRequestPowerIrp](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-porequestpowerirp).
