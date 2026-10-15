# What has been validated

The working demo, source builds and recovery tests provide different evidence.
Use the result that applies to the change you intend to make.

| Check | Result | Scope |
|---|---|---|
| Public dependency retrieval | Passed | Anonymous access to pinned ReactOS/Cromwell commits and RosBE archive |
| RosBE bootstrap | Passed | Fresh private prefix on the development host; complete 6,587-entry receipt |
| Component compilation | Passed | Eight separate profiles, ten component artifacts and the settings utility |
| HAL/network source correspondence | Passed | Historical-compiler reconstructions differ from installed binaries only in timestamps/checksum |
| Windows input dependencies | Passed | Twelve exact matches to owned media; OEM-specific keyboard class documented |
| Supplied Windows ISO identities | Passed | Full SHA-256/SHA-1, every ISO file read, selected full cabinets decompressed; independent Archive.org downloads byte-identical |
| Customized Windows disc clean PC setup | Scoped pass | New blank disk, first logon and media-detached desktop boot; two normal shutdowns, matching 7376 kernel, five clean hives |
| Fully unattended media-test harness | Failed | Setup removed the witness's RunOnce entry; second witness launched manually |
| Complete typed registry decoding | Failed | DRM DataPath type 0x404 unsupported; independent raw key/value comparison passed |
| Retail SP4 clean setup | Pending | Matching retail key required; integrity checks do not establish setup success |
| Customized-disc fresh Xbox assembly | Scoped pass | Fresh PC files/hives, explicit Xbox registry conversion and newly built components on a new standard 10 GB emulator image |
| Fresh assembly file transfer | Strict failure | Eight paths not representable by the current FATX writer; originals retained on the PC disk |
| Fresh audio/network installation | Scoped pass | Genuine SetupAPI installs; subsequent boot exposes one wave device and completes exact 128 KiB TCP transfers in both directions |
| Fresh assembly cold integrity | Scoped pass | Exact persistence data, full allocation, five hive headers/raw values and selected installed code hashes |
| Fresh assembly strict events | Failed | Ftdisk 49, first-boot PlugPlayManager 256 and final-boot kbdhid 1 retained |
| Fresh assembly normal startup | Scoped pass | Automatic diagnostic startup removed; desktop boot and manually invoked checks passed after display installation |
| Offline prepared E installation | Passed | All 6,571 payload files read back exactly in a disposable standard 10 GB image |
| Offline E restore | Passed | Deliberately damaged launcher bytes restored; entire E and both outside ranges verified |
| Restored emulator boot | Scoped pass | Graphics, captured audio, allocation, hives and protected files checked; normal restart |
| Strict restored-system events | Failed | Ftdisk 49 retained; no waiver or event suppression |
| Physical 720p desktop | User confirmed | Clean text and full-window dragging on the tested display |
| Physical 1080i desktop | Defective | Text and motion defects remain; use 720p |

The restored-image test used the prepared demo binaries. The separate fresh
assembly test uses the fresh compiler outputs and Windows files/hives from the
clean customized-disc installation. Neither test qualifies physical deployment
of the new builds. Audio API completion or emulator audio capture does not
replace a physical listener's report or establish exact physical stereo routing.

The [clean-media PC test](windows-media.md) and subsequent
[Xbox assembly](installation.md#validated-clean-media-route-in-the-emulator)
are separate recorded stages. The original typed-decoder and automatic-handoff
failures remain in the evidence. The public media manifest separates these
states from hash recognition and strict qualification.

## Still needed for a general installation release

1. Turn the validated emulator assembly procedure into a portable provisioning
   tool, with an explicit policy for unsupported FATX paths and first-boot device
   setup. A working private image is not distributable and does not resolve
   the failed lossless-transfer, strict-event or typed-registry gates.
2. Exercise the documented build prerequisites on a pristine supported host.
   The launcher currently requires the recorded GCC 12 binary; other compiler
   identities must be reviewed explicitly.
3. Qualify physical installation/recovery separately from the offline image
   test, and resolve or explicitly document the retained strict failures.
4. Review a clean source-only export and its component licenses. Exclude private
   Git history, proprietary files and engineering fixtures before publication.

The project can explain and reproduce its component sources now. It does not
yet promise an automated fresh-console installation or a fault-free system.
