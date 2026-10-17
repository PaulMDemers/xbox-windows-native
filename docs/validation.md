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
| Complete typed registry decoding | Unsupported custom value | Original decoder failure retained; Windows RegQueryValueEx accepts type 0x404 and returns the same 80 bytes as both cold readers. DRM functionality untested |
| Retail SP4 clean setup | Pending | Matching retail key required; integrity checks do not establish setup success |
| Customized-disc fresh Xbox assembly | Scoped pass | Fresh PC files/hives, explicit Xbox registry conversion and newly built components on a new standard 10 GB emulator image |
| Fresh assembly file transfer | Strict failure | Two OEM437 shortcut names restored natively and verified after restart; six genuinely overlong paths remain. Originals retained on the PC disk |
| Fresh audio/network installation | Scoped pass | Genuine SetupAPI installs; subsequent boot exposes one wave device and completes exact 128 KiB TCP transfers in both directions |
| Fresh assembly cold integrity | Scoped pass | Exact persistence data, full allocation, five hive headers/raw values and selected installed code hashes |
| Fresh assembly strict events | Failed | Ftdisk 49, first-boot PlugPlayManager 256 and final-boot kbdhid 1 retained |
| Fresh assembly normal startup | Scoped pass | Automatic diagnostic startup removed; desktop boot and manually invoked checks passed after display installation |
| Windows Media Player video/audio | Emulator scoped pass | Full 3:10 CES clip completed; two video frames independently matched, captured AC97 audio envelope matched the whole source at 0.994 correlation; physical follow-up listed separately |
| Physical Media Player demo | User-confirmed scoped pass | Existing demo: good windowed video, audible audio, a few fullscreen frame drops; normal restart and protected-file readback verified, Ftdisk 49 retained |
| Physical launch routes | Unresolved failure | Menu/FTP attempts returned to dashboard; direct File Explorer launch worked. Live menu target and XBE bytes are correct; no cause or fix established |
| Offline prepared E installation | Passed | All 6,571 payload files read back exactly in a disposable standard 10 GB image |
| Offline E restore | Passed | Deliberately damaged launcher bytes restored; entire E and both outside ranges verified |
| Restored emulator boot | Scoped pass | Graphics, captured audio, allocation, hives and protected files checked; normal restart |
| Strict restored-system events | Failed | Ftdisk 49 retained; no waiver or event suppression |
| Physical 720p desktop | User confirmed | Clean text and full-window dragging on the tested display |
| Physical 1080i desktop | Defective | Text and motion defects remain; use 720p |
| Original RollerCoaster Tycoon / The Sims | Not yet tested | Exact editions, PC controls, API requirements and physical play/save/reload remain to be established |
| Native Direct3D / NV2A acceleration | Not qualified | Current display driver declines DirectDraw; no accelerated driver installed |
| Graphics ladder 00–02 | Modern host, NT5 PC and Xbox scoped pass | Six allowed cases; NT5 and Xbox each verify 129,024 bytes and reject 402 actual-evidence mutations. [Xbox438](../outputs/graphics-xbox438/REPORT.md) retains Ftdisk49 and two shutdown-time rundll32 popups; no primary/D3D/GPU qualification. HAL-only system-memory path remains excluded after the retained host crash |
| Graphics ladder 03 | NT5 PC and Xbox scoped pass | Default/HEL primary presentation with exact HWND clipping, cover/move/uncover and neighboring GDI pixels. Each platform verifies 3,604,480 bytes and rejects 468 mutations. [Xbox442](../outputs/presentation442/REPORT.md) retains Ftdisk49 and two new shutdown rundll32 popups. No scanout/GPU/D3D claim |
| Graphics ladder 04 | Partial NT5 PC pass | Indexed8/RGB565 default and HEL verify 118,784 bytes. RGB32 clipped keyed copies omit pure-red pixels on the 16-bit PC desktop; unresolved, no Xbox rung04 qualification. [444 evidence](../outputs/sprites444/REPORT.md) |

The [1080i investigation](1080i-investigation.md) is paused. Standalone tests
reproduce the defect without Windows, and normal PBKit initialization did not
fix it. Correct captured pixels and raster cadence do not qualify the emitted
fields or identify the responsible device.

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

The [build-to-boot guide](build-to-boot.md) now explains the preparation and
transfer stages. The [graphics roadmap](graphics-roadmap.md) defines the next
game/D3D milestone; it does not change the installation gates below.

1. Turn the validated emulator assembly procedure into a portable provisioning
   tool, with an explicit policy for unsupported FATX paths and first-boot device
   setup. A working private image is not distributable and does not resolve
   the failed lossless-transfer, strict-event or typed-registry gates.
2. Exercise the documented build prerequisites on a pristine supported host.
   The launcher currently requires the recorded GCC 12 binary; other compiler
   identities must be reviewed explicitly.
3. Qualify physical installation/recovery separately from the offline image
   test, and resolve or explicitly document the retained strict failures.
4. Review each public package's contents and component licenses. The repository
   is now public; the history-pattern review and utility kit are documented in
   [tester readiness](PUBLIC-RELEASE.md). Proprietary inputs and private recovery
   data remain excluded from downloads.

The project can explain and reproduce its component sources now. It does not
yet promise an automated fresh-console installation or a fault-free system.
