# Post-mapping SetupAPI paging input diagnostic

Same immutable draw001 fixture, helper, drivers and hives. No guest change.
Adds reviewed VfatGetUserBuffer return capture to the preceding FATX path probe.
EAX is the actual buffer the driver is about to use. EBP locals supply the
already-clipped length and resolved byte offset. Each record links to the
original VfatWrite entry and its return before dispatch completion.

The tracer never invokes a guest mapping routine itself. Raw buffers stay in
private artifacts by SHA256. Observations, returned statuses and exact cold
range comparisons remain separate. Atomic JSON snapshots prevent observers
from reading a temporarily truncated state file. The supervisor waits for
tracer cleanup before permitting runner teardown. No physical-console access.

Run once per attempt; collect only after owned cleanup. Report coverage and
read failures as measured, including retained unmatched entry MDLs. A successful
emulator byte comparison does not identify the physical anomaly's cause.
