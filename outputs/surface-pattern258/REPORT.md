# Dedicated CPU arena works in Windows

The one ordinary emulator run, emu001, launched at 19:39:56 UTC on October 11,
2026, returned to the dashboard at 19:41:28, and completed cold audit at 19:42:09.
No debugger was attached and no physical Xbox access occurred.

The new demand driver allocated its sole16KiB arena at physical address 20008960
in this run. The probe read and verified all16KiB three times across two distinct
CPU writes:49,152 exact bytes. Closing the arena caused further access to be
rejected. The published allocation and retained FileObject intentionally have
no release path until reboot. This bounded diagnostic hold prevents an application
failure from freeing a future renderer target; it is not a production allocator.

The unchanged224 workload then completed64 leases,65 allocations/releases/refusals,
3,194,880 verified bytes, four joined workers and the existing read-only GPU
preflight. Windows shut down normally once and the owned host exited cleanly.
Cold audit found321 directories,6,728 files,322 directory clusters, zero allocation
errors/orphans, five valid structural hives and30 matching protected files.
The new service was absent before boot and present afterward as a demand-start
kernel service with its exact expected ImagePath. Selected storage/display/HID/
crash-dump policies were unchanged. Thirty natural device-binding metadata deltas
remain recorded; this was not a claim of an identical entire SYSTEM hive.

The scoped ordinary CPU arena result passed. Strict qualification remains FALSE
because of the inherited Ftdisk49 error. No new event exception was introduced.
No GL surface was created by this test, and no GPU ownership, pixel-preservation
result, acceleration, physical compatibility or release qualification follows.

## Build and host evidence

Host ASan/UBSan runs execute the actual core and native bridge with host substitutes:
256 allocation races/2,048 contenders,37,748,736 exact byte comparisons, physical
range/translation failures, owner/generation rejection, access limits and
cleanup at failed waits/elevated IRQL. Native build002 passed pinned NT5 import
provider and resident-section review. Build001 passed the host tests and driver
compile but failed on a probe indentation warning; original sources and logs
are preserved, with no guest launch from that build.

Driver SHA-256:
eba5d954d9075700a1a94b8196377626862bf74767b0bfbfe5c104d528a457a1.
Probe SHA-256:
6919e19a5ec4d1feb37e75e6a928a9abc8f342d8b23838bf230625e49694b677.

The future pixel oracle specifies a13x11 BGRA8 texture with64-byte stride inside
the arena,572 pixel bytes and15,812 guard/padding bytes. Nine negative controls
reject stale contents, overwritten guards, a wrong pixel, wrong stride, flipped
rows and swapped red/blue channels. These are host oracle tests, not executed GL
tests. The expected bytes are independently generated, never read back from the
renderer under test.

Preparation used the historical phase250 immutable seed, adding two diagnostic
files and a startup call before the unchanged224 workload. No hive was edited
during preparation. The actual emulator is the established685f24e3 build, not
the new257 scalar-instrumented build. See lineage-review.json for inherited
descriptive fields that do not apply to this new child. Neither emulator fixture
is a validation of the current physical audio-integrated demo.

Closed portable copies227/231/232/233/257 were archived with full hash verification
and original-path junctions, recovering approximately980MB on C. No disk images
or backing chains moved. The20GiB build guard remains unchanged. Physical
audio004/software-video118/shared158/FATX0101, the256 recovery bundle, original0088
and immutable0.1.0 remain untouched.
