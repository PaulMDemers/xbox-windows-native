# Input trace 006

Continue the bounded, read-only diagnostic from inputtrace004/PROCEDURE.md with
the identical immutable veto source and unchanged guest payload. Preserve003's
wrong arm address,004's incomplete trace/host INF-reference error and005's
preflight-only rejection.

Additional sites observe keyboard and mouse class enable-helper entry/return.
Addresses come from004's module observation and are checked against exact
provider identity, RVA, header and relocated bytes on a hit. Observe forwarded
CREATE dispatches and share checks while a class helper or class-originated
IoGetDeviceObjectPointer call is active. Retain every kernel-open caller address
and refresh module lookup before classifying an external caller; do not assume
cached driver ranges still identify a newly loaded driver.

Inspect extension/class/lower-device identity, input IRP and file objects,
helper return status, and any actual sharing checks reached. Unknown reads
remain explicit. Static alternate paths and names alone do not prove ownership.
No guest code/data/register write command exists. Breakpoints and single steps
affect timing, so ordinary boot/timing qualification remains false.

The host INF is copied as bytes and explicitly pinned to d8b50e1f6e49c7a3d1a0aea3a4fee0219351c9be8b7f8121ab02ab47d8c53e83.
The observer and host bounds, cooperative leases and mandatory cold audits
remain as before. Report trace coverage separately from package/workload gates.
