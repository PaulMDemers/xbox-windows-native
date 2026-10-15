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
| Offline prepared E installation | Passed | All 6,571 payload files read back exactly in a disposable standard 10 GB image |
| Offline E restore | Passed | Deliberately damaged launcher bytes restored; entire E and both outside ranges verified |
| Restored emulator boot | Scoped pass | Graphics, captured audio, allocation, hives and protected files checked; normal restart |
| Strict restored-system events | Failed | Ftdisk 49 retained; no waiver or event suppression |
| Physical 720p desktop | User confirmed | Clean text and full-window dragging on the tested display |
| Physical 1080i desktop | Defective | Text and motion defects remain; use 720p |

The fresh compiler outputs were not substituted into the restored-image test.
That test used the current prepared demo binaries. It does not qualify those
new outputs for deployment. Emulator audio capture also does not replace the
physical listener's report or establish exact physical stereo routing.

The [clean-media PC test](windows-media.md) does not yet qualify a fresh Xbox
assembly. Its original typed-decoder and automatic-handoff failures remain in
the evidence. The public media manifest separates these states from hash recognition.

## Still needed for a general installation release

1. Assemble a bootable installation from the user's Windows materials through
   a documented workflow, including exact kernel/input dependencies and registry
   configuration. The prepared private payload is not distributable.
2. Exercise the documented build prerequisites on a pristine supported host.
   The launcher currently requires the recorded GCC 12 binary; other compiler
   identities must be reviewed explicitly.
3. Qualify physical installation/recovery separately from the offline image
   test, and resolve or explicitly document the retained strict failures.
4. Review a clean source-only export and its component licenses. Exclude private
   Git history, proprietary files and engineering fixtures before publication.

The project can explain and reproduce its component sources now. It does not
yet promise an automated fresh-console installation or a fault-free system.
