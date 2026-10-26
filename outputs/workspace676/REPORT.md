# 676 Workspace archive and documentation audit

Storage maintenance only, authorized October 26, 2026. The current technical
boundary remains [timer675](../timer675/REPORT.md). No Xbox, firmware, VM or
driver experiment was launched by this maintenance pass.

## Completed result

All 221 selected files were verified, their durable records reconciled, and their
individual original copies removed. Transfer exited 0 with no transfer errors.
All owned archive/test processes are closed.

| Measure | Result |
| --- | ---: |
| Source content archived | 107.989 GiB |
| Archive content on D: | 106.293 GiB |
| Existing Zstandard streams moved unchanged | 186 |
| Newly compressed captures | 35: 2.077 GiB to 0.381 GiB |
| C: free after cleanup | 69.706 GiB |
| E: free after cleanup | 83.075 GiB |
| D: free after cleanup | 359.234 GiB |

Observed C:/E: free-space increases total about 106.79 GiB. That measurement can
differ from logical source bytes because of allocation and concurrent system
activity; the exact before/after byte readings are in [closure001](closure001.json).

## Inventory and selection

The scoped inventory covered the repository plus its known C:/xwn* and E:
artifact/archive/build directories: 500,949 regular files, no traversal errors,
and 87 reparse paths skipped rather than followed. This is not a full-machine
inventory. The existing Ubuntu backing VHD is on C: and is preserved.

D: is a healthy, online, approximately 466 GiB exFAT volume connected through
a USB SATA bridge. The private destination is
`D:/Xbox-Windows-Archive/2026-10-26`.

The reviewed plan selects 221 old files totaling 115,952,365,361 source bytes:
existing compressed disk/capture evidence and 35 log/RAM captures needing
compression. Selection excludes current/recent working inputs, tracked files,
protected recovery/release material and all raw virtual disks. The plan was
validated in full before execution. The transfer's final totals are recorded
in `closure001.json`.

Raw QCOW headers were inspected separately: 1,560 headers and 1,166 backing
references in the scoped inventory. The first private audit incorrectly treated
POSIX names as Windows paths. `backing-audit002.json` preserves that failure and
corrects `/mnt/<drive>` translation; three WSL-only paths remain outside its
resolution scope. No raw disk was selected or moved on the basis of that audit.
SDKs, sources, live disk chains, WSL storage, current 674/675 inputs and private256
recovery stay in place.

## Archive and recovery procedure

The authored helper copies existing `.zst` streams byte for byte, compresses
selected `.log`/`.trace`/`.ram` captures, hashes the archive, fully decodes it,
and re-hashes the original. It records a receipt, source-side pointer and journal
event before removing that individual source file. No recursive deletion or
directory move is used. All source directories remain. Private pointers are
excluded from Git.

Each archive is held on D: under a source-path identifier. Exact original paths,
archive/source/decoded hashes and sizes are in the private receipts. The D:
root contains a pinned standalone restore helper and guide. Two real retained
artifacts were restored to fresh inspection files and matched their recorded
source hashes, one for each mode; those owned inspection copies were removed.
Full archive verification does not constitute a restored Windows boot.

This is file-content preservation, not an NTFS ACL/alternate-stream/hardlink
backup. No historical report or closed runtime is rewritten or reopened.
See [archive and restore instructions](../../docs/ARTIFACT-ARCHIVE.md).

## Repository and documentation findings

A separate documentation agent audited maintained guides and the repository's
current evidence. The updated guide map separates software rendering, game
compatibility and native acceleration; it corrects stale RCT save/load/scrolling
claims, records 480p and 1.6 limits, and removes instructions to rerun closed624.
Historical reports, frozen bundle instructions and prior failures remain intact.

Strict `tools/xwn.py verify` failed on four existing launcher source pins:
`xwn_hd_adapter.c`, `xwn_hd_native.c`, `xwn_hd_profile.c` and `xwn_hd_profile.h`.
These files and `upstream/components.json` were not changed by this maintenance.
The [build guide](../../docs/building.md) now exposes the mismatch and keeps
source/manifest promotion separate. No `--allow-modified` waiver was applied.

Validation performed:

- Nine archive helper tests passed, including corrupt archive, changed source,
  low-space and failed-receipt preservation, plus exact restoration.
- Repository host suite: 137 tests, 10 skips, passed.
- Working-tree scan: 44,760 tracked files passed binary/media/credential-pattern
  checks. This is not a new full-history provenance audit.
- Independent helper/recovery review found no blocking defect for this selected
  stopped-writer batch. Its archive-directory prerequisite was added to the guide.
- Final staged checks and transfer closure are retained in this kit.

The console's last known state remains dashboard674, no hook; it was not polled
or contacted for storage maintenance. Physical lease/firewall state is retained,
build lease was free, and automation remains paused. Protected720p, XBOX480,
releases and recovery are unchanged. Boot/1080i, Ftdisk49/Popup26 and the prior
timer/SMC/UDP uncertainty remain unresolved.
