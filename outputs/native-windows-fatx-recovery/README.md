# Scoped physical FATX recovery

This kit preserves and repairs only the damaged Windows/test allocation records
identified by the full-F preflight. It is not a general filesystem repair utility.

## Physical result — 5 October 2026

Recovery and the first candidate 0088 short hardware trial **passed**. Windows
completed cached append, all 30 mapped/truncate cases, 32 MiB asynchronous
pressure and the 15-second idle interval, then restarted normally to UnleashX.
FTP verified every test payload and the unchanged filesystem driver, trace
miniport and HAL. The post-reboot audit again passed all 3,439 immutable binaries
and nine registry hives. The independent full-F scan found zero allocation
errors or orphan clusters across 128,105 live entries.

System event records 60–64 are new relative to the prelaunch capture. They contain
normal EventLog start/stop and no delayed-write events. The existing Ftdisk 49
error remains; there are no application records in this trial's time window.
Automatic startup is disabled, the console is on the dashboard, and all owned
emulator processes are closed. The next test is a separate controlled 300-case,
five-minute hardware soak. The earlier physical STOP 0xA is not yet proven fixed.

## Recovery method

The physical backup contains 557 exact 64 KiB clusters, including all affected
chains, their directory clusters and the orphan. The full FAT matches the
previous capture. Raw bytes stay in ignored local artifacts; tracked manifests
pin hashes, entry locations and the repair scope.

The five-sector plan changes only directory entries. It detaches five damaged
Windows files by setting their first cluster and size to zero. The shared
32 MiB test-file chain remains allocated. Two new preservation entries retain
the 37-cluster WMI chain and the one orphan cluster. The FAT does not change,
and no data clusters are freed or overwritten. The offline full-metadata audit
then has zero errors and zero orphans, with all unrelated entries unchanged.

`repair.c` compares the entire FAT snapshot and every target sector before any
write. Each target must match the recorded before or after bytes. It flushes and
reads back every 512-byte write. The original and reverse plans remain preserved.
These checks support recovery from a completed-sector prefix; they do not make
multi-sector writes atomic against power loss or repair a torn sector.
The reverse plan describes the pre-restoration state. It must not be applied
after restoration or later Windows writes; the full-FAT precondition now differs.
Completed physical operations are one-shot records and must not be relaunched.

The unchanged native executable passed three owned-emulator tests: normal apply,
rejecting a stale second-sector expectation without any F write, and resuming
when the first sector is already in its final state. Cold comparisons check the
entire F write extents, not only the requested sectors. No unplanned changes or
FAT changes occurred. Emulator low-LBA I/O validates the engine; the exact physical
high-LBA plan is separately validated against the real backup.

Physical launch records and independent postscan results are recorded separately.
The repair verified and applied all five planned sectors, including four above
LBA28, and returned to the dashboard. The independent rescan exactly matched the
offline rehearsal: zero allocation errors, zero orphans and an unchanged FAT.

`restore-windows.py` can restore only four zero-length detached entries: the
qualified 0088 filesystem driver, both original WMI repository files, and the
System Information shortcut. It pins source hashes, preserves the physical HAL
and trace miniport, and keeps Windows startup disabled. MMC3.tmp remains an empty
temporary file. Restoration completed and every file matched its pinned bytes.
The subsequent audit passed all 3,439 immutable Windows binaries and nine
registry hives. A fresh full-F rescan covered 128,100 live entries in 6,058
directory clusters, with zero allocation errors or orphan clusters.

FTP readback also confirmed the preserved 32 MiB test chain, old WMI chain and
orphan contents exactly match their pre-repair raw backups. These preservation
files remain allocated on F; they are not reused as working Windows data.

The dashboard's slow large-upload behavior first affected an E staging file,
before repair launch. That upload was stopped after verifying launch had not
occurred. The already captured FAT file was renamed within E into the repair
folder, with complete byte verification; the host copy and another on-console
copy remain intact. See `verification-file-reuse.json`. No partial upload was
accepted as verification data. The same transfer behavior recurred during WMI
restoration before any Windows launch. Restoration resumed only after validating
the destination as an exact prefix of the pinned source. Separate 32 KiB
STOR/APPE transfers resolved the stall, with complete readback afterward.

`physical-trial.py` runs one bounded test using the already qualified helper:
cached append, 30 mapped/truncate cases, 32 MiB asynchronous pressure and a
15-second idle interval, followed by normal restart. It archives the previous
reports and test files, preserves event logs, checks launcher/driver hashes,
and disables automatic startup before collecting the result. It never retries
a launch based solely on an uncertain FTP reply. A clean short result does not
establish that the earlier five-minute hardware crash is fixed.

Evidence is split by phase:

- `physical-backup.json`, `backup-request.json`: preserved raw cluster scope.
- `repair-plan.json`, `rehearsal-allocation.json`: exact offline plan and audit.
- `engine-*-validation.json`: emulator apply, rejection and resume checks.
- `physical-repair-validation.json`: real disk exactly matches the rehearsal.
- `restoration.json`, `restored-audit.json`: restored files and preboot audit.
- `physical-restored-allocation.json`: full allocation audit before the trial.
- `physical-trial.json`: actual launch, report, payloads and driver readback.
- `physical-trial-allocation.json`: independent full allocation audit afterward.
- `posttrial-audit.json`, `physical-trial-qualification.json`: final post-reboot
  binary/hive audit and combined bounded-test verdict.

Raw clusters, Windows files, firmware, hives and disk images remain ignored local
artifacts. Only source, hashes, manifests and reports belong in the repository.
