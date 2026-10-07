# Mapping growth, allocation shrink and regrowth

New emulator-only regression from the settled0101/video0093 parent. No driver
or hive change. The inherited QEMU null package and01B0/01B4 failed-install flags
remain explicitly audited before/after, not physical support. Strict event errors
remain failures. This kit does not reproduce or explain the original physical
non-ASCII111-byte corruption merely by exercising the same logical boundary.

Four rounds across11 deterministic files make792 mapping/appending/truncation
cycles. The mapping extends35 bytes beyond the intended final EOF. Prefixes near
65536 and131072 force32 expected AllocationSize decreases, queried before and
after SetEndOfFile through the owned NT5 NtQueryInformationFile export. File size
and allocation must match the reviewed FATX cluster rounding. First append,
second append/regrowth and final append are reopened and checked:132 full-byte
reopens. All11 final files also require independent cold byte/allocation checks.
Intermediate AllocationSize is the filesystem's report, not an independent raw
FAT-chain snapshot. The full cold scan verifies final allocation ownership.

serial001 is the ordinary serial control. flush001 uses the SAME executable,
fixture/startup/data and2ms dirty-mapping dwell, adding a volume FlushFileBuffers
worker. It performs no raw volume reads/writes, lock or dismount. The worker's
start/end observations must lie inside the SAME unique append epoch to count an
overlap; each of44 file-rounds requires positive overlap. This proves temporal
coverage of an append lifecycle, not simultaneous execution at a specific kernel
instruction. Stop/join occurs after mappings and file handles close; exact single
object wait success is required. Worker errors/timeouts or absent overlap fail.

Establish and cold-audit serial001 before launching flush001. Launch once per
unique attempt; never reuse logs or seeds. A pending-install hold is not a passed
workload. All source/compiler/import/oracle identities must be pinned before
launch, and fixture/allocation/PnP checks must pass. No debugger or UI action is
planned. Any held/failed guest remains evidence for diagnosis, not a reason to
silently relax the oracle or edit drivers. Raw inputs/binaries/disks stay private.

check-oracle.py proves expected shrink coverage and rejects missing cases/shrinks,
missing overlap, failed query, worker timeout, short verification count, missing
restart and trailing failure. This is a harness check, not guest validation.
Independent cold event/hive/protected-file/allocation gates are in audit.py.
Normal-shutdown count and actual dashboard return are both required. No new
warning/error event is waived, even when exactly repeated from the fixture.
