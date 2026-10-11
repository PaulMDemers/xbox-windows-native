# First genuine resource-only PnP trial — closed

The exact 01B4 package installed successfully, but the live device remained at
Code 10. Probe exit23 correctly stopped before any lifecycle or restart request.
Installation API success alone did not qualify START_DEVICE.

The disposable emulator ran19:36:37–19:39:37UTC on2026-10-10 and was stopped at
the180-second host bound. This was not normal shutdown; no dashboard return or
event6006 was recorded. Do not relaunch this closed fixture.

Installed SYS/OEM-INF bytes match build001. The cold review passed protected
files, five hive structural checks, old SetupAPI/event history and FATX allocation
(319directories,6725files,320directory clusters, no errors or orphans).
The full binding delta is retained; global configuration equality and whole-boot
success are not claimed. Inherited Ftdisk49 remains a failure.

The resource-only driver contains no port-I/O instructions and rejects telemetry.
The compiled power path had a readiness-ordering concern; power-review.md records
the finding and lifecycle002 repairs it. Neither power nor removal was exercised
here. The baseline HAL was retained. No physical-console access occurred.

Evidence: build001.json, build-review001.json, emulator001/run.json,
emulator001/audit.json and emulator001/pnp-review.json.
