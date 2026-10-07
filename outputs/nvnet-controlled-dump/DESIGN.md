# A real dump after the resident network shutdown correction

This is a fresh disposable crash003, never a restart of the two closed failures.
Preparation requires both new ordinary NVNet comparison cases to pass strict
workload, TCP, normal shutdown and cold integrity gates. It stages only reviewed
NVNet0104 over the immutable dump-map fixture; FATX0103, HAL0102, video0093,
HidServ, dump settings and emulator-only device policy remain unchanged.

The exact earlier one-shot helper/trigger and cookie remain. The observer pins
actual candidate NVNet code at the intended bugcheck, observes shutdown entry,
idle-helper entry and paired shutdown return, then the existing callback-list
return and genuine dump path. It never forces a return or changes guest data.
All breakpoints are removed and the guest resumes after a bounded capture.

Successful execution still requires cold PAGEDUMP plus the exact bugcheck
parameters at the independent high-LBA pagefile location, dump return status,
write-trace evidence and unchanged 28-bit alias. Preserve the crash image.
Only a separate recovery child may then boot to collect/recover the dump.
No physical qualification or original corruption-cause claim is implied.
