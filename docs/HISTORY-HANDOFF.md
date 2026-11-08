# Xbox research history handoff

This document describes the handoff procedure and planned locations. It does not by itself establish that staging, verification, or the external copy has completed. Check the final overview and its referenced manifests and logs for the actual status. Older receipts under Save are historical records; where they conflict, the final overview supersedes them.

## Planned staging locations

- `C:\Users\Paul\Desktop\Save`
- `D:\Save-Xbox-History`
- `E:\Save-Xbox-History-E`

The drive-relative directory layout is mirrored under `history\C`, `history\D`, and `history\E` in the appropriate staging folders. Preserve the directory trees and manifests when copying. The D: staging folder also contains `WSL-research-history.tar.gz`, intended to preserve three WSL research trees. A full WSL operating-system and Windows-toolchains TAR is excluded; those environments are reconstructible. Consult the final overview for archive completion and validation.

## Inventory and verification

`tools\history-handoff.py` reads a JSON plan containing an array of absolute source and destination directory pairs. For example:

```json
[
  {"source": "E:\\research", "destination": "E:\\Save-Xbox-History-E\\history\\E\\research"}
]
```

Run commands from the repository directory, and substitute the actual plan and manifest paths. Place each manifest outside all roots in its plan. Inventory creates a new output file exclusively; choose a new name after a failed attempt. Errors are fatal, and a manifest without a completion record cannot pass verification. The tool inventories and verifies only: it does not move or delete data.

Before a same-volume directory move, record a metadata baseline:

```powershell
python tools\history-handoff.py inventory --plan E-plan.json --output E-before-metadata.jsonl --metadata-only
```

After the move, verify that baseline against the mapped destinations:

```powershell
python tools\history-handoff.py verify --manifest E-before-metadata.jsonl --location destination --metadata-only
```

This checks the recorded paths, file sizes, and modification times, plus directory and file totals. It does **not** hash or prove file contents. Once moves are complete, create a full SHA-256 inventory of the destinations:

```powershell
python tools\history-handoff.py inventory --plan E-plan.json --output E-after-sha256.jsonl --location destination
python tools\history-handoff.py verify --manifest E-after-sha256.jsonl --location destination
```

Repeat for each actual plan. A metadata-only manifest requires explicit `--metadata-only` verification and cannot be used as a full SHA-256 verification. Reparse points cause inventory to fail by default. `--allow-reparse` records their targets rather than following them; verify the records and their significance before relying on them for recovery.

## External copy and recovery

Copy **all three** staging folders, their plans, manifests, logs, and the final overview to storage outside C:, D:, and E: before wiping those disks. An on-disk inventory does not verify that external copy. On the machine holding the external copy, run full SHA-256 verification against the copied folders before wiping. For example, if the E: staging folder is copied to `F:\XboxArchive\Save-Xbox-History-E`:

```powershell
python tools\history-handoff.py verify --manifest F:\XboxArchive\E-after-sha256.jsonl --location destination --rebase E:\Save-Xbox-History-E F:\XboxArchive\Save-Xbox-History-E
```

For a portable copy of a tree containing NTFS junctions, use `robocopy` with `/E /XJ` so junctions are excluded and never traversed, for example:

```powershell
robocopy E:\Save-Xbox-History-E F:\XboxArchive\Save-Xbox-History-E /E /XJ
```

For a manifest made with `--allow-reparse`, add `--skip-reparse` to verification **only for a copy made with `/XJ`**. The verifier skips junction records and ignores the actual reparse-point count, while continuing to hash every recorded ordinary file and check ordinary file and directory totals. The manifest retains the recorded link targets; restore links separately if needed. This option does not verify link presence or targets on the copy. It is not a substitute for copying the separately preserved junction targets.

Adjust the manifest and new root paths to the actual copy. `--rebase OLDROOT NEWROOT` maps a recorded path prefix to the copy; repeat the option if a plan has multiple mapped roots. Perform equivalent verification for the C: and D: manifests, including an appropriate SHA-256 check of the WSL archive if it is not covered by a manifest. Keep the successful verification output with the external copy. Investigate any missing files, mismatches, errors, or incomplete manifests before relying on the archive or wiping disks.

For restoration, copy the desired trees back while preserving their layout, then verify them against the SHA-256 manifests using the appropriate `--location` and `--rebase` mapping. QCOW images can contain absolute parent paths: restore the original namespace, or rebase a **disposable copy** of the image chain with appropriate tools. Do not modify the archived originals or launch archived closed tests.
