# Recovering an archived historical artifact

Cleanup328 preserves old disk/trace bytes in a `.zst` file beside their former path. The adjacent `.archived328.json` receipt records the original and compressed SHA256 hashes. Original frozen experiment reports remain unchanged.

To restore one file, use the receipt's absolute path:

```powershell
C:/Python314/python.exe -B outputs/storage-trim328/restore-file.py 'E:/path/to/hdd.qcow2.archived328.json'
```

Run from this repository. Restoration verifies both hashes, refuses to overwrite an existing file, and retains the archive. An optional `--output E:/xwn328/verification-copy.qcow2` writes a separate verification copy instead. Do not launch or modify an old test disk merely because it has been restored; create a new authorized fixture as usual. Restore the exact original path when an old audit expects it. Backing parents were not selected for archival.

Deleted duplicate emulator executables have `.deduplicated328.json` receipts. Copy the retained `canonical` file back to the recorded `target` only if needed, then check it against the receipt's SHA256. E: is exFAT, so the cleanup did not create hardlinks. Sources, unique builds and canonical binaries remain.

The two removed WinDbg installer downloads have `.pruned328.json` receipts. The extracted debugger and symbols remain; every extracted file was checked against `work/microsoft-dump-reader/provenance.json` before pruning. Those downloads need not be restored to use the existing debugger.

The cleanup scripts use consumed batch IDs and must not be rerun. `archive-manifest.json`, `prune-manifest.json` and `result.json` record completed work. Private inventory, QCOW dependency graph and intent/completion journals remain under E:/xwn328.
