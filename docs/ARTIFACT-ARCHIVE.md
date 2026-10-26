# Local artifact archive and restoration

The development machine's archive disk is **D:**. It is unrelated to Xbox
partition letters. The October 26, 2026 archive lives at
`D:\Xbox-Windows-Archive\2026-10-26`. This is private evidence storage, not a
public download, a new release, or a dependency for building from source.

The archive contains selected old captures and previously compressed virtual-disk
evidence from C: and E:. Existing Zstandard files retain their exact compressed
bytes. Other selected log, trace and RAM captures are compressed with Zstandard.
Raw virtual disks and their backing chains are left in place, along with current
source/build inputs, SDKs, WSL storage, recovery files and release packages.
The [workspace audit](../outputs/workspace676/REPORT.md) records the final scope
and measured storage result. Historical attempt records retain their original
paths and hashes.

## Find a file

At each removed source path, look for a sibling named
`<original-filename>.archive-location.json`. It records the original location,
archive location, source/archive SHA-256 hashes, sizes and compression mode.
The original directories are retained.

The D: archive also contains:

- `plan.json`: the explicit selection and its original size/time pins.
- `receipts/`: one verified receipt per archived file.
- `files/`: compressed content, named by an identifier derived from its source path.
- `journal.jsonl`: verified-copy and source-removal events.
- `inventory.jsonl` and `inventory-summary.json`: the scoped pre-cleanup inventory.
- `summary.json`: the completed transfer totals and storage readings.

These indexes are private. They can describe Windows, game, firmware or captured
memory content and must not be committed or bundled into a public source release.
Do not edit an old report merely to replace its historical path: use the pointer
or index to find its archived bytes.

## Restore for inspection

Use Python **3.14** (the archive helper uses its standard-library
`compression.zstd`). From the repository root in PowerShell:

```powershell
python tools/archive-artifacts.py restore `
  'D:\Xbox-Windows-Archive\2026-10-26\receipts\<id>.json' `
  'C:\private-inspection\original-filename'
```

Create the destination directory first and choose a new, nonexistent output
file. A sibling `.archive-location.json` can be supplied instead of the receipt.
The helper checks the compressed archive hash before writing, verifies restored
content against the source hash, and refuses to overwrite an existing file. It
requires the destination volume to retain 20 GiB free after restoration.

For `compress-zst`, restoration decodes the archive to the original capture.
For `relocate-zst`, restoration returns the original **compressed** file, byte
for byte. Follow that historical artifact's own decompression and dependency
instructions if an uncompressed copy is needed. Restoring evidence does not
reopen a closed runtime or qualify it as a parent for a new test.

This is a content archive. Original modification time and basic Windows
attributes are recorded; the helper restores modification time but does not
restore ACLs, alternate data streams, hardlink relationships or other NTFS
metadata. D: is exFAT. Keep live checkouts, SDKs and WSL backing storage on their
existing filesystems.

## Perform a future archive pass

1. Read the latest continuation and inventory active processes, leases, disk
   space, current build inputs and recovery dependencies. Age alone is not
   sufficient evidence that an artifact is expendable.
2. Create a new archive directory on the destination volume. Prepare a private
   JSON plan with that `archive_root`, `allowed_roots` and a
   `files` list. Each file specifies `path`, `bytes` and `mtime_ns` from a fresh
   inventory. Keep raw virtual disks, backing chains and protected inputs out.
3. Review the complete selection, then dry-run:

   ```powershell
   python tools/archive-artifacts.py archive 'D:\archive-pass\plan.json'
   ```

4. Copy/compress and verify with `--execute`. Add `--remove-verified` only when
   source reclamation is intended. The helper supports `.zst`, `.log`, `.trace`
   and `.ram`; it refuses other formats, symlinks/reparse paths, changed source
   pins, duplicate selections and existing destination records.
5. Check the journal and actual free space. Before removing each individual
   source, the helper verifies its archive, fully decodes the Zstandard stream,
   re-hashes the source, and writes durable receipt/pointer/journal records.
   It never recursively deletes directories. Stop writers while archiving;
   the tool is not a filesystem snapshot or a concurrent-writer lock.

If a run fails, preserve its error log, partial archive and original files.
Reconcile receipts, pointers and source existence before preparing a fresh
remaining-files plan; do not blindly rerun the original deletion plan. Failed
verification never authorizes removing that original. The synthetic recovery,
corruption and mutation tests are in `tools/test-archive-artifacts.py`.
