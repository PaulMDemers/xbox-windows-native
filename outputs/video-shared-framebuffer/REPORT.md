# Shared uncached framebuffer: ordinary emulator pair passed

The new0106 prototype keeps boot-video's permanent uncached4MiB mapping and
lets the desktop miniport borrow its pointer. The freshly reconstructed UC
control and shared-UC candidate both passed the same ordinary drawing workload
and all cold gates. No debugger was attached and no UI intervention occurred.
Physical hardware was not contacted or changed.

| Evidence | Control001 | Candidate001 |
| --- | --- | --- |
| Windows launch UTC | 20:35:43 | 20:38:09 |
| Dashboard return UTC | 20:37:26 | 20:40:01 |
| Drawing cases / exact pixel stages | 54 / 162 | 54 / 162 |
| Normal shutdown events | 1 | 1 |
| New warning/error/application events | 0 | 0 |
| Full F allocation | 324 directories,6755 files,325 directory clusters; no errors/orphans | Same |
| Structural hives / protected files | All5 parsed / all matched | Same |
| Configuration and96MiB pagefile | Unchanged | Unchanged |
| Shared-pointer trace | Absent, as expected | Acquire SUCCESS,FCED6000,physical03C00000 |
| Trace records / dropped | 43 / 0 | 44 / 0 |

See pair-review.json and each case's audit.json, closure.json and frozen source
snapshot. Both attempts are CLOSED; never relaunch or recollect them. The trace
contains one successful acquisition, but no release/unload event. Ordinary
shutdown therefore does not prove that the provider's release path ran in guest.

## Implementation and build

Fresh RosBE reconstruction from0093 tree329a29d61af1620a9fc00579185000483379837
plus0106-shared-uc-framebuffer.patch produced tree
53e9aedc58152d03116c00579185000483379837. The matched builds differ only in
XBOX_NT5_SHARED_FRAMEBUFFER OFF/ON. Only the miniport and boot-video override
differ between guest fixtures. Microsoft framebuf, FATX0103, HAL0102, NVNet0104,
ATAPI0105, HidServ, mode1024x576x32 and probe107 remain identical. Existing
emulator-only QEMU null-device and01B0/01B4 failed-install policy is retained.

The provider publishes a44-byte descriptor once from the boot initializer and
uses a spin lock for bounded desktop-owner reference accounting. Geometry,
physical range, cache type and requested address are checked. The permanent
boot mapping survives zero desktop references and unload accounting; consumers
cannot free or replace it. Old11 boot-video export ordinals remain intact. Three
new exports are imported through the actual loader name bootvid.dll. PE review
resolved every import against owned NT5 binaries; the successful ordinary boot
and provider trace then exercised the new import path on Windows2000.

The actual provider C source passed80 host boundary/lifetime checks and400000
concurrent acquisition attempts with8 joined workers.124579 accepted references
were released successfully; ASan/UBSan/leak checks reported no errors. The host
shim models exclusion, not NT5 scheduling. Publication is intentionally single
initializer before consumers. pe-review.json pins source/test/executable hashes;
host-test-environment.json records commands. Probe provenance is documented
separately: build-review.json is the unchanged historical probe review.

## Limits and next discriminator

This establishes ordinary boot/drawing/normal restart with the shared UC pointer.
It does not establish exhaustive PTE/TLB alias removal, crash-renderer behavior,
generic PnP stop/remove safety, or physical throughput. There was no cache-policy,
PAT/MTRR, PTE, mode or device-policy change. No WC or speed improvement is claimed.
InbvCheckDisplayOwnership is only an acquisition precondition; counted references
do not make drawing quiescent.

Next use a new bounded read-only diagnostic to compare the provider pointer and
boot-video globals, pin live code, inspect ownership order and enumerate actual
resident aliases. Then validate crash rendering in a sacrificial child before
reviewing a coordinated WC transition. Keep the completed128GiB recovery result,
original physical111-byte anomaly, and prior failed evidence separate.

Build94303, preparations65504/7944, runners9310/61900, supervisors84264/75140 and
audits33224/55417 are all CLOSED. No owned emulator remains. C free23850192896
bytes at closure;20GiB build guard is unchanged. Two closed standalone older
runs were hash-verified to E with original-path junctions; see
../task-storage-offload/manifest-20261007d.json. No backing chain was relocated.
