# What has been validated

The working demo, source builds and recovery tests provide different evidence.
Use the result that applies to the change you intend to make.
The [current status and guide map](current-status.md) summarizes the latest
engineering boundary; the table below retains both completed and failed gates.

| Check | Result | Scope |
|---|---|---|
| Public dependency retrieval | Passed | Anonymous access to pinned ReactOS/Cromwell commits and RosBE archive |
| RosBE bootstrap | Passed | Fresh private prefix on the development host; complete 6,587-entry receipt |
| Component compilation | Passed | Eight separate profiles, ten component artifacts and the settings utility |
| Current checkout strict source verification | Passed after review 677 | Four stale launcher hashes and the reference tree reconciled to retained 633 evidence, two fresh strict builds and six compiled-wrapper fixtures; all eight profiles verify. No source edit or gate waiver; 676 failure preserved ([build guidance](building.md#current-checkout-launcher-pins-reconciled)) |
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
| RollerCoaster Tycoon Deluxe | Native Xbox title/menu, windowed Forest Frontiers, building, manual save/load and arrow/right-button scrolling observed; persisted save checked across normal restart. Three editions rendered in PC controls ([details](rct-compatibility.md)) | Window-edge view stays still; fullscreen, sustained play and Xbox FPS unqualified; sound deferred. Exact scripted physical scene restoration is distinct from manual save/load |
| RCT graphics/process measurements | Scoped PC results | Sampled saved-scene GDI DIB presentation and PC628 timer caller observed, with host-checked process costs; no physical game-cost/FPS result or acceleration proof ([measurement boundary](rct-performance-plan.md)) |
| Physical 480p profile | Scoped drawing and interactive pass | 720×480×32 drawing in 638, Notepad dragging/save/reopen in 642, same file reopened under 720p in 643; boot intermittency remains |
| Explicit 480p selector | Transfer/restore pass, boot failure retained | 645 apply/readback and 720p restoration passed; 480p boot returned black. 646 recovery desktop passed; no live Windows switching or automatic selection ([details](display-mode-switching.md)) |
| Additional-console inventory | User-supplied 1.6 schema-2 report validated | Encoder unidentified, cable/HD-setting context incomplete, Windows unqualified; hardware testing deferred ([matrix](console-compatibility.md)) |
| Original The Sims | Not yet tested | Exact edition, PC control, API requirements and physical play/save/reload remain to be established |
| Native Direct3D / NV2A acceleration | Not qualified | Current display driver declines hardware DirectDraw callbacks; no accelerated driver installed |
| Graphics ladder 00–02 | Modern host, NT5 PC and Xbox scoped pass | Six allowed cases; NT5 and Xbox each verify 129,024 bytes and reject 402 actual-evidence mutations. [Xbox438](../outputs/graphics-xbox438/REPORT.md) retains Ftdisk49 and two shutdown-time rundll32 popups; no primary/D3D/GPU qualification. HAL-only system-memory path remains excluded after the retained host crash |
| Graphics ladder 03 | NT5 PC and Xbox scoped pass | Default/HEL primary presentation with exact HWND clipping, cover/move/uncover and neighboring GDI pixels. Each platform verifies 3,604,480 bytes and rejects 468 mutations. [Xbox442](../outputs/presentation442/REPORT.md) retains Ftdisk49 and two new shutdown rundll32 popups. No scanout/GPU/D3D claim |
| Graphics ladder 04 | Complete NT5 PC 24-bit and Xbox 32-bit scoped passes | All six cases verify 174,080 bytes; [Xbox452](../outputs/sprites-retry452/REPORT.md) completed normal restart. Original 16-bit failure and 451 missing receipt remain |
| Graphics ladder 05–09e | Scoped software controls on NT5 PC and Xbox | Lifecycle, discovery, triangles, textures, depth, transforms, combined scenes and presentation; selected-input alpha arithmetic passes but ideal endpoints fail. Sustained-scene Xbox clock checks pass; PC QPC durations unqualified. See the [per-rung matrix](graphics-samples.md#the-ladder) for exact limits |
| Graphics ladder 09f | NT5 PC scoped pass; Xbox incomplete | Perspective interpolation passed PC controls; 557/558 produced no physical sample receipts |
| Timer/UDP diagnostics | Physical 674 no datagrams; 678 host-only full-firmware timer integration | Lights-off/black observed at 674, followed by manual reset. 678 passed 25 isolated full-image function fixtures and 313 review checks; timer/SMC code unchanged, no sender call or physical qualification ([report](../outputs/timer678/REPORT.md)) |
| RGB32 key diagnostic | Complete observation; keyed semantics fail | Both backends pass plain copies; three keys fail with/without clipping,134 pixels/backend. Full key values retained; all pixels match low16 comparison model, implementation not traced. [446 evidence](../outputs/key-semantics446/REPORT.md) |
| RGB32 key diagnostic at24-bit desktop | Scoped NT5 PC pass | Exact446 binary passes both backends and92,160 bytes after verified16→24-bit switch; original mode restored. The initial Xbox attempt produced no receipt and remains a separate failure. [447 evidence](../outputs/key-depth447/REPORT.md) |
| RGB32 key diagnostic on Xbox 32-bit desktop | Scoped physical pass | Default/HEL each pass 12 stages; 92,160 bytes exact, 19,592 mutations rejected; normal restart and unchanged 720p baseline. Ftdisk49 and one shutdown popup retained. [449 evidence](../outputs/key-retry449/REPORT.md) |

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
