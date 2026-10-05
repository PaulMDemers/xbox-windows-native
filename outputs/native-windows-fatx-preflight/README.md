# Next physical test: read-only F: integrity preflight

This kit is ready to collect the full FAT and live directory records before any
repair or Windows boot. It opens Xbox Partition6 with GENERIC_READ only and
writes its reports beside its own XBE on E:. It does not touch C:, the softmod,
the Windows startup file, partition geometry, or F: contents.

The emulator validation checked every captured entry against the stopped source,
independently verified complete directory coverage, and found no F: write extents.
The analyzer was also challenged with a free driver chain, a crosslink and
incomplete captures. A completed capture does not mean that the disk is healthy.

The launch script requires the two candidate qualification reports (r14/r15),
the verified preflight XBE, the console ownership marker, and the existing
no-op Windows startup hash. It refuses an existing launch or app directory.
The local `check` command validates these gates without contacting the console.
Set XWN_FTP_PASSWORD in the environment for launch/collection, then run:

```powershell
C:/Python314/python.exe outputs/native-windows-fatx-preflight/physical-preflight.py check
C:/Python314/python.exe outputs/native-windows-fatx-preflight/physical-preflight.py launch
# After the console returns to the dashboard:
C:/Python314/python.exe outputs/native-windows-fatx-preflight/physical-preflight.py collect
C:/Python314/python.exe outputs/native-windows-fatx-preflight/analyze.py --capture outputs/native-windows-fatx-preflight/artifacts/physical-001 --output outputs/native-windows-fatx-preflight/physical-allocation.json
```

The read-only hardware run completed on 5 October 2026. The Xbox accepted FTP
launch, captured the metadata, and returned to dashboard FTP without manual input.
The retrieved completion record reports6058 directory clusters and128098 entries.
The host audit reconstructs6053 directories and122046 files. See
`physical-preflight.json`, `physical-allocation.json` and `recovery-scope.json`.
Do not relaunch this one-shot capture or boot the damaged Windows install.

The777 audit records describe six affected Windows/test files, not777 separate
files. There are387 unique shared clusters between the prior32 MiB test file,
MMC3.tmp and the System Information shortcut. The driver and two WMI files have
invalid or undersized chains. One allocated cluster has no live owner. No
allocation conflicts were found outside the owned Windows/test files; unrelated
file contents have not been verified. The full FAT SHA-256 exactly matches the
previous physical013 snapshot, confirming these allocation findings predate
this read-only scan. No F repair was performed.

The next step is to preserve raw contents for the affected chains and orphan,
then rehearse a bounded metadata repair offline. Never use ordinary FTP deletion
on these crosslinked entries: that could free another file's storage. Restore
Windows files only after disentangling ownership and checking the result.

The result determines the recovery scope. Preserve the existing corrupt driver
and WMI capture. Check ownership of every affected cluster before freeing or
replacing anything; inspect errors outside the Windows tree separately. Restore
Windows-owned files from verified source/backup material only after that review,
then audit binaries and hives. Do not reformat F: or delete unrelated files.

After recovery, stage the qualified filesystem candidate while retaining the
known physical HAL and video miniport. First use a short test with automatic
return to the dashboard and independent payload/hash checks. Extend to the same
dirty replacement, handle/mapping and idle workload only after that bounded pass.
The synthetic emulator fixture is not a clone of this physical disk, and the
original physical STOP0xA has not been conclusively attributed.
