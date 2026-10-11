# Isolate the extra rebalance events

Three fresh standalone emulator fixtures start from the same immutable wizard201
base. All use stop001's exact driver, INF, installer and candidate ownership HAL.
One newly built helper is identical across cases; only XWN_REBALANCE_MODE in the
startup command differs: 0 skips rebalance, 1 permits one rebalance, and 2 vetoes
one QUERY_STOP. The helper records guest UTC FILETIME and uptime at lifecycle
boundaries and leaves a ten-second observation interval after the selected action.

Every case retains the property-change, power, CANCEL_REMOVE and safe-removal
checks. Each case gets one launch, a 180-second host bound, its own disk/EEPROM
and local ports, then a cold audit. No physical access, changed network settings,
warning suppression, automatic setup dismissal, debugger or root-fixture
integration occurs. Shared build and exclusive emulator leases serialize work.
An action failure stops the pipeline; only pre-action lease contention is retried.

The driver emits the same resource-state flags as stop001. This asks the PnP
manager for a resource rebalance and can involve other devices; it does not
fabricate PnP IRPs. Expected target minor counts are zero QUERY_STOP/STOP/CANCEL_STOP
for skip; one QUERY_STOP and one STOP for allow; one QUERY_STOP and one CANCEL_STOP
for veto. All cases must recover for subsequent resource-only operations.

Message identification uses actual installed provider bytes, not an event-number
guess. extract-messages.py opens the immutable stop001 source fixture read-only,
resolves EventMessageFile from its system hive, and pins each provider. The
Windows-side decoder reads PE message resources for the exact full event IDs.
Input event data is decoded as IO_ERROR_LOG_PACKET; FinalStatus is offset 20 in
this NT5 x86 layout, corroborated by the installed class drivers' error-writing
instructions. The observed 0xC0000043 is STATUS_SHARING_VIOLATION. Static inspection
finds IoGetDeviceObjectPointer in an enable-helper path, but does not prove that
this path supplied the observed status or identify a conflicting owner.

The comparison requires exact driver/HAL/probe pins, startup-only arm differences,
genuine PnP trace sequences, target recovery, protected bytes, five hives,
complete E:/F: allocation and preservation of previous log history. Event times
and raw guest FILETIME values are retained. Their epoch values agree directly;
both guest UTC displays run four hours ahead of the host. Subtracting the frozen
guest registry's ActiveTimeBias of 240 minutes places all helper marks within
their host run intervals. Guest-relative event correlation uses raw epochs with
no timezone subtraction; absolute guest clock accuracy remains unqualified.
The first host review mistakenly described a FILETIME/event discrepancy and
applied a conditional subtraction to only the helper. Its source/result remain
preserved with review-correction001.json; review002.py corrects the interpretation
without rerunning a guest. The event log's one-second resolution is retained.
A single case per arm can establish a controlled association; it cannot
establish an intermittent failure rate or identify an input handle/network packet.

Primary references:

- [Resource rebalance can involve multiple devices](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/stopping-a-device-to-rebalance-resources)
- [IO_ERROR_LOG_PACKET fields](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_error_log_packet)
- [NTSTATUS definitions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55)

Whole-boot, functional input/network, SMBus transactions, terminal takeover,
normal restart, repeated-boot persistence and physical qualification remain
separate gates. Pending APU setup is retained. Used fixtures stay closed.
