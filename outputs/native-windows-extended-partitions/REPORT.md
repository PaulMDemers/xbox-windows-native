# Extended F partition development — October 4, 2026

FreeLoader successfully read a 4,097-byte file from synthetic FATX F: at
absolute byte offset **145,644,445,696** (LBA **284,461,808**), above the
LBA28 limit. Run `extended-read-001` reached **XWNF90**, verifying the full
pattern, length, EOF and a cross-sector seek, then halted before Windows.
No debugger edits were used. The host harness stopped the owned emulator.

This is loader read validation only. The revised HAL compiles and all 84
imports resolve against the selected Windows 2000 kernel; its extended-table
path has not yet run under Windows. No new Windows storage binary was uploaded
to the physical Xbox. The verified physical XWN390 boot-screen baseline remains.

## Why the partition changes are needed

The physical inventory reports a 250,059,350,016-byte drive and F: starting at
LBA 15,633,072, covering 472,764,096 sectors, with 64 KiB clusters. Its free
space is approximately 94.65 GiB. Existing loader/HAL code only represents the
five stock Xbox partitions. Its old E: extent would overlap this F: by 24,912
sectors. Merely changing the Windows boot path to partition(6) is insufficient.

Patch 0063 introduces a shared bounded PARTINFO parser in the loader and HAL.
A valid table supplies every active extent, including E: and F:. Invalid
magic-bearing metadata fails closed. With no table, the previous five-partition
fallback remains; F: is never guessed. Unknown flag/reserved-field extensions
and gaps in active numbering are currently unsupported and rejected.

The HAL requests exact device length with IOCTL_DISK_GET_LENGTH_INFO before
accepting extents. Early Windows 2000 support for that request remains untested;
failure returns an error rather than trusting rounded CHS capacity.

## Evidence and reproduction

- `test-parser.c`: valid 250 GB layout and exact capacity accepted; truncated,
  overlapping, overflowing, reserved-field and unsupported layouts rejected.
  GCC `-Wall -Wextra -Werror -fsanitize=address,undefined` passed, including
  30,000 mutated sectors.
- `patch-check-0063.json` and `patch-check-0064.json`: both full patch chains
  verified through `tools/apply-series.py --verify-only`. They branch from
  verified patch 0059; experimental rename patches 0060–0062 are excluded.
- `Build.ps1` / `build.sh`: pinned RosBE release build in isolated
  `reactos-extended` worktree; `XBOX_NATIVE_EXTENDED_READ_PREFLIGHT=ON` is opt-in.
- `prepare-read-fixture.py`: compressed private 250 GB fixture with a sentinel
  in cluster 2,100,000. Source hash preserved; no physical disk operations.
- `package-read-probe.py`: no Windows media; hard stop before kernel entry.
- `validation.json`, `read-fixture.json`, `iso-manifest.json`, `hal-audit.json`
  record exact artifacts. Screenshot retained locally under `evidence/`.

## Shadow C and physical follow-up

Rocky5's published NKPatcher disk-image driver sets a virtual partition's
StartingOffset to the physical disk end. That matches the reported C: boundary
exactly, supporting the user's Shadow C explanation. It does not identify the
installed softmod revision. Pinned primary sources are in `REFERENCES.txt`.

The separate metadata application has been uploaded to
`F:\Applications\XWNMetadata\default.xbe`. It reads sector 0, the BRFR marker
sector, and the F: superblock through read-only handles, writes its own report,
then reboots. Its subsequent physical `physical-cycle-001` report accepts the
six-entry PARTINFO table and confirms the same extents as this emulator fixture.
Use that validated metadata path for further emulator Windows storage tests.
Do not interpret shadow C: offsets as raw disk extents, replace partitions,
format F:, or start Windows writes on this disk at this stage.

The older emulator BIOS reports a 128 GiB-capped capacity to Xbox applications
even with a 250 GB fixture. The metadata probe correctly rejected the larger
table against that capacity. FreeLoader's own ATA path nevertheless passed the
high-LBA read. This distinction is why firmware and Windows paths need separate
validation.

Host disk exhaustion interrupted an initial fixture copy. Only reproducible
task-owned metadata fixture/run copies were reclaimed; source hashes and
reports remain. The compressed high-LBA fixture is retained for continuation.
