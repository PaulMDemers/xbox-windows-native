# Physical F deployment and isolated E launcher

This kit stages a native Windows 2000 installation in previously absent F paths,
and a separate `E:\Applications\XWNFBoot` launcher. It does not format or change
the partition table. The physical `E:\Applications\XWNLoader` XWN390 baseline
and existing games remain separate from this installation.

Physical deployment completed on 4 October 2026: all 6,493 files, 681,704,691
bytes, passed readback. The final loader and launcher also passed readback.
At 18:20:52 UTC, UnleashX accepted one `SITE EXEC` launch. FTP was available
when checked afterward, but neither result file existed on dashboard C, E or
F. The user subsequently confirmed Windows appeared, with black/white text
over it, and the console rebooted into UnleashX. The text was not photographed
or identified, so neither successful probe execution nor native writes are
established. No second launch was sent. `enable-desktop.py` has not been run.
Next: print explicit file-operation errors and use a separately pre-created
report to distinguish new-file creation from in-place writes.

## Evidence and limits

The exact launcher and startup probe reached the Windows desktop in ordinary
xemu run `nt5-physical-f-package-003`, without debugger changes. The probe read
65,537 known bytes, created a separate 65,537-byte file, flushed and reopened it,
verified every byte, and requested a normal Windows restart. Screenshots show
the desktop and the subsequent UnleashX dashboard. A cold audit verified the
probe's PASS record, test payload, 3,439 immutable Windows binaries, registry
trees and allocation ownership, with no orphan allocations or crosslinks.

The capture harness timed out while inspecting the rebooted dashboard. Emulator
FTP control and forwarded passive data connections work, but the stock
Complex4627 dashboard exposes an empty, incorrectly sized F volume for this
large-disk fixture. Results were retrieved offline; this is **not** a successful
emulator FTP result-retrieval cycle. The physical UnleashX already exposes the
large F volume and is accepting/readback-verifying the installation files.

Physical native Windows storage success is not established by emulator results.
See `physical-cycle-001.json` and `physical-native-result.txt` only after a real
launch and fresh report retrieval. A successful startup probe demonstrates
native Windows user-mode and storage operation; it does not alone establish
that the Explorer desktop is visibly correct on the physical display.

## Loader fixes

Patch 0067 adds opt-in `XBOX_NATIVE_FATX_F_BOOT`, default OFF. It locates stage 2
under the isolated E launcher while the Windows root remains partition 6.
Patch 0068 pins each successfully mounted ARC backing-device slot until loader
handoff. The loader caches filesystem dispatch after closing individual files,
but its FATX mount state is indexed by device slot. Reusing that slot for F
overwrote the cached E volume state and made a valid HAL path return ENOENT.
Both `ArcOpen` and `FsGetVolumeSize` mount paths now retain one mount reference.
There is no unmount API in this loader; mounts are bounded by the available
device slots and cease to matter after kernel handoff. Failed mounts are not
pinned. The change is enabled only with the new physical F option.

Run 001 stopped because the application directory was absent from the boot
path. Run 002 and debugger scout 005 identified the cached-volume issue. Scout
results are diagnostic evidence, not reproducible boot success. Run 003 uses
the compiled fixes and no debugger. The default-OFF rebuild matches baseline
executable bytes after excluding only PE checksum and export timestamp fields;
HAL and rosload remain byte-identical to the validated 0066 artifacts.

The complete source chain is in `patch-check-0068.json`, based on ReactOS
`afc0127e8f937ab68503d715d948844973756aa1`, resulting tree
`b6226e9439275ac4ec86d9d3bb161f619d562d79`. Experimental rename patches 0060-0062
are excluded. No Windows or Xbox binary payloads are committed.

Physical FTP rejected creation of `WINNT\com+.log` with error 450. This is a
384-byte informational COM+ text log, not a program or registry hive. The
uploader preserves its identical bytes as `WINNT\com-plus.log`; the original
package manifest stays unchanged and the transfer report records the remote
name. All executable and configuration payloads retain their original paths.

## Deployment safeguards

`prepare-package.py` extracts the validated native F image, preserves empty
directories, and installs a dedicated startup probe. The original package
manifest is immutable once deployment starts. `upload.py` reserves absent
destination roots with an ownership marker and verifies every uploaded file by
full byte readback. A partial existing file must be an exact package prefix to
resume. The launcher is uploaded as `launch-held.xbe` so partial installs cannot
be launched from the Applications list.

The UnleashX server needs `CWD` followed by `LIST`; a path argument to `LIST` is
ignored. Small 32-KiB transfers using 1-KiB socket writes with TCP_NODELAY avoid
the server's severe transfer stalls. Connection failures can be resumed from
verified prefixes. No global network settings are changed.

`activate-launch.py` requires all package files verified and emulator PASS.
It also requires fresh physical report/test paths to be absent, installs the
exact revision-003 loader with readback, preserves the original staged loader,
then renames the held XBE. Before issuing `SITE EXEC`, it writes a durable
launch-attempt record. It never repeats an uncertain launch automatically.
Credentials come from `XWN_FTP_PASSWORD`, not the repository.

`run-cycle.py` waits for the verified upload, invokes activation once, and then
performs bounded retrieval attempts after a 60-second restart wait. It records
its state and never retries a launch. `enable-desktop.py` is a separate,
PASS-gated action: it backs up the owned startup command, disables the probe's
automatic restart, and sends one launch for physical display/input testing.

`probe.c` uses CREATE_NEW for its report and write test, checks the expected
Windows path and 64-KiB large FATX geometry, and limits its test writes to owned
paths. Ordinary Windows boot also writes its registry/profile/system files on
F. Windows sees this native FATX volume as C; the dashboard still calls it F.
This is direct native filesystem access, not a virtual disk inside a file.
`collect-physical.py` retrieves and validates the new report and payload after
normal reboot. If the kernel hangs before user-mode, a physical photo/reboot is
still required; FTP cannot service requests while Windows owns the hardware.

## Reproduction

Use the shared console build lease through `Build-Launcher.ps1`, `Build.ps1`
and `Build-Probe.ps1`. Apply the complete recorded ReactOS chain with
`tools/apply-series.py` in a clean pinned checkout. `prepare-emulator.py
--revision 003` creates a fresh private fixture from the retained normalized F
source. Run it with the usual diagnostic harness, physical launcher alias,
64 MiB, native autorun, guest reboot enabled and disk retention.

After shutdown, `native-windows-extended-storage/audit-cold.py --run
nt5-physical-f-package-003` validates the result. `record-emulator.py` records
the verified cold result and screenshot identities without claiming FTP
retrieval. The optional `collect-emulator.py` creates a private loopback passive
data forward, but cannot fix the stock emulator BIOS's F geometry limitation.

Generated media, installation package, build products and full traces stay
local. Retired private fixtures are identified by hash in the retirement
reports; the source fixture, successful run disk and physical baseline remain.
