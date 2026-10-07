# Missing HID service restored in two isolated emulator runs

October 7, 2026. Both attempts CLOSED and cold-audited. No debugger/UI action,
physical access, driver change or registry/device-policy alteration. The owned
hidserv.exe was added to fresh children of the preserved settled0101/video0093
parent; test helper/status queries are described in README.md.

| Result | serial001 | flush001 |
|---|---:|---:|
| LaunchUTC |08:10:32|08:15:35|
| Dashboard returnUTC |08:12:55|08:17:58|
| HidServ state / Win32 exit / service exit, start and end |4/0/0|4/0/0|
| Appends / queried allocation shrinks / reopens |792/32/132|792/32/132|
| Exact final cold files |11|11|
| Complete volume flushes |0|799|
| Complete flushes in append / dirty epochs |0/0|353/305|
| Bounded dirty-map rendezvous |0|44|
| Successful worker join / errors |0/0|0/0|
| Normal shutdown count |1|1|
| New SCM7000 events |0|0|
| New Ftdisk49 events |1|1|
| Workload and cold integrity |PASS|PASS|
| Strict qualification |FAIL|FAIL|

Every concurrent file-round has positive append/dirty overlap. Full allocation
scans both report323 directories,6765 files,324 directory clusters and zero
errors/orphans. All five hives parse; the restored service, dependencies, FATX,
video, kernel and boot payload hashes remain exact. Initial hives were unchanged.
No new application/popup records exist. The formerly missing service now reports
SERVICE_RUNNING with zero errors at both checkpoints, while its corresponding
startup error disappears under both workloads. This supports the missing-file
diagnosis for this emulator fixture; it says nothing new about live hardware.

Ftdisk49 is still a strict failure, without waiver. The exact message identifies
pagefile configuration for crash-dump use. Follow ../baseline-event-forensics
for static candidate sites and the necessary runtime discrimination. No dump
configuration was disabled. This correction is not a release qualification,
physical recovery snapshot or explanation of the original111-byte corruption.

All owned sessions closed: preparation32329/32845; serial runner49325,
supervisor47255,audit68697,configuration/closure56932; concurrent runner4633,
supervisor38870,audit99598. Sources/binaries/fixtures/28 parents/cold artifacts
are pinned per case. Do not relaunch or recollect. Earlier missing-service
fixtures and every failed test remain preserved.
