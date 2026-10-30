# Active direction: fixed 720p Windows boot on Xbox 1.6

User explicitly stopped the mode-setting probe campaign. Mismatch832 is stopped
source-only: never build, stage or launch it under this continuation.

Review found Windows miniport and bootvid already retain firmware geometry and
support 1280x720x32. Their shared contract is physical03700000, nine MiB reserved,
retail64 MiB. Kernel frontend establishes720p successfully. The new launcher must
retain that mode, move only scanout base into the existing reservation, and avoid
the legacy encoder/timing initialization and destructive128 MiB RAM probes in
both Xromwell and FreeLoader. Preserve the existing Windows display drivers.

Dashboard independently authenticated. Read-only inventory833 found no standard
Windows E installation or F volume. Prepare an isolated stock-E installation from
the owned immutable343 package with exact pins and create-only/readback staging.
Check current E geometry and free space before allocation; do not access Xbox C.
Capacity834 is installation preparation, automatic dashboard return, no mode test.
Then build fixed720p boot835 from pinned source-only677/334 parents, validate the
retained-video contract and boot chain, stage and launch once after readback.

831 CLOSED FAIL (native phase5/error9), already collected once and pushed30e71f1b.
No hook or host runtime. Never reopen closed attempts. Old automation stays paused;
direct user authorization continues. No claim of Windows boot on1.6 yet.
