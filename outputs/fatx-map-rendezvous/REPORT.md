# Both bounded workloads complete; strict event failures retained

October 7, 2026. Both fresh attempts are CLOSED and fully cold-audited. No
debugger, UI action, driver/hive change or physical console access in either.

| Evidence | serial001 | flush001 |
|---|---:|---:|
| LaunchUTC |07:52:45|07:56:39|
| Dashboard returnUTC |07:55:02|07:58:57|
| Completed appends |792|792|
| Queried allocation-size decreases |32|32|
| Full immediate reopens |132|132|
| Exact final cold files |11|11|
| Successful volume flushes |0|810|
| Complete flushes within an append epoch |0|347|
| Complete flushes within dirty mapped residency |0|331|
| Successful bounded rendezvous |0|44|
| Worker join / error |0/0|0/0|
| Normal shutdown events |1|1|
| Full allocation errors/orphans |0/0|0/0|
| Structural hives / protected hashes |PASS|PASS|
| Bounded workload and integrity |PASS|PASS|
| Strict qualification |FAIL|FAIL|

Every concurrent file-round has positive append and dirty-mapping overlap;
the minimum dirty count is1. Both complete allocation scans record323
directories,6764 files and324 directory clusters. All five hives parse.
Final bytes agree between modes and the independent expected round3 data.
Preflight source snapshots, helper/compiler,28 backing parents, fixture,
closure/disk and raw cold evidence hashes verify. comparison.json records them.

Each strict failure is exactly the inherited SCM7000 HID Input Service %%2 and
Ftdisk49 HarddiskVolume6 error; no new application/popup records. These remain
failures. This is not a release qualification or physical recovery promotion.

Unlike the preceding failed coverage attempt, this helper explicitly waits for
the first dirty-map flush of every file-round with a10-second limit; the other
17 appends continue racing. The serial mode substitutes100ms first-map dwell.
This changes scheduling and is not a timing benchmark or exact scheduling
control. Positive overlap proves temporal API containment, not that a particular
page reached the hardware during that call. AllocationSize decreases are API
observations; the final FAT ownership scan is independent.

All failure paths attempt stop/join and retain ABORT_JOIN. Neither run entered
that path; its runtime behavior is not certified by these successful runs.
The normal and abort waits are separately bounded60seconds; a failed normal
join can trigger another60-second abort join. Synchronous I/O itself can still
hang, hence the outer owned-host deadline. Do not claim a hard60-second global
cleanup guarantee. Source review/import checks and11 negative oracle checks
passed, but synthetic negative logs are not execution of those failure paths.

Prior ../fatx-map-truncate/flush001 remains a failed overlap run with post-timeout
diagnostic capture and host termination. These results do not erase it. Neither
pair reproduces the physical111-byte non-ASCII damage or identifies the original
restart method. The separate intentional interruption's111 zero bytes remain
a different byte pattern and evidence class.

Owned sessions closed: serial runner72749/supervisor18673/audit27289; flush
runner4280/supervisor39796/audit34783; paired verifier79466. No guest, tracer,
observer or collection remains active. Never relaunch/recollect these cases.
