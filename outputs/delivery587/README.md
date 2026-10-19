# Private Xbox transfer kits and storage recovery

The user resumed work after the October 19 cutoff and requested space recovery,
the pending save/load control, and two ZIPs for their own other Xboxes. The
scheduled automation remains paused. PC586 save/load evidence is recorded in
the adjacent rct586 directory; this directory records delivery and capacity.

## Delivered private files

Both are in `E:/Xbox-Test-Kits/2026-10-19`, with SHA-256 sidecars and a shared
START-HERE.txt. Extract each ZIP into a separate PC directory: each has its own
versioned host verifier. Copy only the contents of E to dashboard E.

| Kit | ZIP bytes | SHA-256 |
| --- | ---: | --- |
| Xbox-Hardware-Info.zip | 7208064 | 24a52f961bddd1911dcf7003a606b8b5c997ebd90a0c275a3a21d2e0c942011d |
| Windows-2000-Xbox-E720p.zip | 326861540 | 3130dc218a0114f7f16326ec22b2a920de2c1b0e6ff28c0a4e97c4653151b814 |

Hardware kit reuses the exact qualified421 package: compiled safe-PCI inventory
XBE, report validator, source, notices and instructions. It writes a numbered
E/xwn-report JSON. No keys, serials, MACs or EEPROM are requested.

Windows is a fresh read-only snapshot of the development Xbox's ordinary
installation and matched boot chain. The active Xromwell launcher, modified
DLLs/drivers, hives and startup bytes are unchanged. Two inactive .422used
loader backups were excluded and retained privately. The two exact files in
xwndemo372 required by ordinary startup are included. RCT/media/saves/test
launchers are excluded. Installed payload is 707763829 bytes; target E needs
at least 1.25 GiB free. ZIP payloads, CRCs, manifest, source tree and seven
hive checks passed. No other-console installation/boot/removal is qualified.

The private Windows ZIP retains the user's existing profile and licensing data;
it must not be published. All binaries, hives, captures and ZIPs stay outside
Git. The public WINDOWS-README.txt explains first hardware inventory, backup,
binary FTP, launcher-last/readback verification, watched boot and removal.

## Space recovered without discarding experiment evidence

dedup001 attempted a hard link on E, which is exFAT. The operation failed and
the renamed original was immediately restored. dedup002 verified 17 identical
closed emulator executables against one retained canonical copy, then removed
the duplicates. Its catalog records every original path and hash; 3253207040
bytes were recovered. No disk, log or configuration was removed in that step.

The complete dependency inventory enumerated 855572 WSL directories and
2678377 files, finding 29 QCOW headers. archive001 also checked scoped C/E
QCOW headers and found no children referencing the five selected closed disks.
585/584/582/581/578 disks were compressed to E/xwn587/archives, decompressed
and independently hashed against the originals before the C copies were
removed. Archives retain every original byte and path. These closed runtimes
may be restored for evidence inspection only, never relaunched or parented.
Earlier bounded inventory timeouts and the hard-link failure remain recorded.

Only newly created delivery capture/staging duplicates were removed after the
Windows ZIP was verified. The two excluded originals and full capture manifest
remain private. No console files were deleted or written. No physical launch
was sent; dashboard FTP and protected720p were verified during the snapshot.

## Evidence

- dedup-plan001, dedup001, dedup002: exact restoration/failure records.
- backing-inventory001 and archive001: dependencies and round-trip archives.
- console-probe001, capture-plan001, capture001, supplement001: read-only source.
- windows-stage001, windows-hives001, windows-package001: private ZIP checks.
- utilities001: exact qualified hardware package verification.
- staging-cleanup001: bounded new staging cleanup after ZIP verification.

The archival receipt began with C free at 21058560000 bytes, below the 20 GiB
target, and ended at 24064831488; the reason for the intervening host-space
drop is not established. Archival wrote to E with a 20 GiB guard, and new VM
phases were admitted only after the 21 GiB check including the WSL backing
volume passed. Do not describe the reserve as continuously maintained.
Boot intermittency, Ftdisk49, shutdown popup
limitations and unqualified encoder/layout combinations remain. No GPU, game
FPS, or physical save/load claim follows from packaging or PC controls.
