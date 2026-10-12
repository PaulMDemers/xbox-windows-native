# Xbox Windows 2000 0.2.0 — private experimental HD release

This release adds boot-selected **720p and 1080i** to the existing audio-enabled Xbox Windows 2000 demo. Both profiles completed physical drawing and audio workloads, normal shutdown, and subsequent allocation, hive and protected-file checks. The user reported a correct-looking 720p desktop and, for the 1080i run, “The video output had looked normal at 1080”.

The supported scope is the tested **Conexant console with its HDTV-capable connection**, using the audio004/softwarevideo118/shared158/FATX0101 installation as the upgrade baseline. Other encoders and HDMI adapters need separate validation. Rendering remains software-based; resolution is chosen before boot.

## Packages

- `xwn-0.2.0-hd-overlay.zip`: matched six-file 720p and 1080i profiles, the six pre-test baseline files, instructions, hashes and qualification record.
- `xwn-0.2.0-private-demo.zip`: the same overlay, instructions and qualification record, plus the existing demo256 system and boot/dashboard recovery ZIPs and their original manifest. These are unchanged historical recovery copies, not a newly captured HD installation.
- The tagged source/evidence archive and Git history bundle are generated separately from `v0.2.0`; their exact revision and hashes are recorded in `source-evidence-bundles.json` after tagging.

Read **USAGE.md** before installing. Packaging does not deploy anything. The console remains on its restored pre-test baseline; no hardware test is queued. The private recovery material contains owned operating-system files and user data and must not be published as a public source distribution.

## Evidence and limitations

| Evidence | Result and scope |
| --- | --- |
| Physical 720p, watched trial315 | Five drawing samples, six audio phases, normal shutdown, clean allocation and hive/protected checks; user saw a correct picture |
| Physical 1080i, trial324 | Five 1920×1080×32 samples at pitch7680, six audio phases, normal shutdown; 6221 directories, 122676 files, 6226 directory clusters, zero allocation errors/orphans; five hives and protected/policy/binding checks passed |
| User report after324 | Normal-looking video at1080; TV OSD mode identification and exhaustive field/artifact testing were not separately confirmed |
| Matched emulator trial323 | Unchanged guest reached the HD workload after the reviewed PRAMDAC register-storage correction; this is separate emulator evidence, not physical performance proof |
| Private recovery256 | 6638 files / 879661149 uncompressed bytes, readback-verified at capture; original archive hashes reverified during packaging |

**Strict qualification remains false because of the known Ftdisk49 event.** This experimental release does not waive that gate or rewrite closed test results. The historical WAVE_MAPPER output-ID diagnostic failure is retained; audible tones do not establish exact stereo routing. Unsupported-device prompts may remain. The earlier314 early boot return remains unexplained; the watched retry does not establish repeat-boot reliability.

This is not a whole-disk backup, bare-metal installer, full restore validation, power-loss guarantee, GPU acceleration release, or Windows runtime mode-switching implementation. The release packages exact tested binaries; it does not claim a new full compiler rebuild or byte-identical full-system reproducibility. Emulator migration schema changes compiled successfully but were not exercised by a save/restore test. Existing `v0.1.0`, original0088 rollback, staging325 and every failed experiment remain unchanged.

## Next work

1. Make deployment and recovery repeatable: baseline comparison, readback verification, then a separately planned restore test and repeated HD boots.
2. Resume measured physical video performance work, preserving the visible software-rendering fallback. Native GPU ownership and cache/lifetime requirements remain unresolved.
3. Integrate device-wizard cleanup and audio improvements through the existing chats, with shared hardware scheduling and separate validation of stereo routing.
4. Prepare component-specific build recipes and a sanitized public source export; review the independently supported xemu changes for upstream submissions.

No further experiment, deployment or public publication is triggered by this release.
