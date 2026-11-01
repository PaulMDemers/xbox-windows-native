# Historical fixed video configurations and bundle pins

Profiles are selected at boot. None offers live Windows mode switching. The legacy original development console (Xbox 1.0 lineage, Conexant) is distinct from both the current Xbox 1.6 target used in 842/843 and the separate user-reported 1.6 inventory device in 630.

## Original development Xbox (Xbox 1.0 lineage)

| Profile | Physical Windows evidence | Qualification | Package pins |
|---|---|---|---|
| 1024x576 | Two physical Windows boots passed graphics pixel checks, bounded timing loops, normal restart/EventLog6006, driver/helper hashes and trace validation. | Video-only repeat-boot scope; no full allocation/hive audit or extended storage soak. Non-HD F-based chain. | Miniport SHA `3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf`; source tree `329a29d61af1620a9fc005b0d8fcfb9e1a937d20`; private overlay SHA `44c613e74b8a82e1494cc60140e3ceee27d53df4762e1ede97e22800242857e5`; see `outputs/video-trace-reuse-settled/`. |
| 720x480p | Physical watched Windows load/desktop/pattern/restart in 638; user confirmed Notepad save/reopen and mouse dragging in 642; ordinary 720p return in 643. Windows reported 720x480x32@60, stride 2880; three GDI cases had zero mismatches. | Scoped interaction and selected file/hive integrity; no full FATX scan. No live switching or published selector support. | Loader SHA `a53a09427f80411efee73ef53da0ec9829f8af0d27d404f5a3ff818e96b4bde4`; exact staged chain in `outputs/windows480p642/stage001.json`; source pins in `outputs/windows480p642/runtime-pins001.json`; candidate report `outputs/native480p633/REPORT.md`. |
| 720p | Physical Windows profile/workload on original development console; released as stable HD baseline for tested Conexant/HDTV setup. | Supported fixed boot profile on the legacy target. | v0.2.0 overlay `D:/Codex-archive/xbox-windows-native/0.2.0/xwn-0.2.0-hd-overlay.zip`, SHA `474957aa6d2eb4cd8c3818a26ad0568e4b9c104b8159891c065b1491c8f6930d`; launcher SHA `c2bd899182caf0f076f8999feac1f48457fc4e6ad201ec358c06781f5740945f`. Later private E snapshot ZIP SHA `3130dc218a0114f7f16326ec22b2a920de2c1b0e6ff28c0a4e97c4653151b814` (not tested on other consoles). |
| 1080i | Physical Windows workload in 324 and phase-attribution runs in 347. | Experimental: later visible text/field/drag defects unresolved. | Same v0.2.0 overlay SHA; launcher SHA `bd8e58f2e1c934074b15d3df1208f9caa7acb22243325083f26a7fe9fd30daf6`. Source revision `25b41b7ea47850cab21c649d9661ffd18497348e`; source/evidence ZIP SHA `7dec63ec58b9c9e2d880b375f4abe1df5c18c3fbdaf5ea0666de9dd5c5b4143f`; history bundle SHA `17921714e66988b75a3c967190e4a4dc578eca4baf6f696d2b9230cd7d883ccb`. |

The 640x480 registry default is not counted as a verified physical Windows mode: the effective mode was not measured. The v0.2.0 overlay is a matched six-file profile overlay with baseline restore files, not a complete E installation. Shared overlay hashes are listed in `inventory.json` and exact entries in `outputs/release-0.2.0/bundle.json`.

## Current Xbox 1.6 target (842/843)

Fixed 1280x720x32@60 reached the Windows desktop in physical 842 and again in 843. Mouse connected before 843 boot worked. Shutdown hung; user manually restarted, so clean shutdown is not qualified. Exact source trees: Cromwell `8936f433027bbbeb5ad27572c96c758836f433ae`, ReactOS `507946208da61a2811726cdeed35bad0b3ff2505`, FATX `deb06b15f2723645f9572cc372e16431d5c9ea3d`. See `outputs/boot720-bridge842/desktop-profile001.json`, `launch-source-pins001.json`, and `outputs/boot720-input843/REPORT.md`. Runtime candidate hashes in the profile manifest include exploratory diagnostics and are not a ready release payload.

The separate user-reported 1.6 inventory device in 630 is not the 842/843 target: its report has GPU e1/MCP d5 and unidentified encoder. No Windows profile follows from that inventory alone. No Windows qualification for 480p or 1080i on 1.6 was found.

## Package cautions

The targeted offline comparison of stock E and the legacy 642 pre-test SYSTEM hives is recorded in `registry-semantic-comparison.json`; it found matching selected video defaults and FATX service settings, while the full hives differ. It does not qualify the new 1.6 package.


* The 587 private E/720p ZIP is an original development-console snapshot; it does not prove 1.6 compatibility.
* The v0.2.0 source archive and profile overlay are legacy Conexant-console artifacts. The overlay is not a complete Windows E image.
* Keep firmware, EEPROM, BIOS, dashboard, Windows media, and user profile data out of public source archives.
* Keep a separate fixed profile in each bundle and record the exact resulting archive hash.
