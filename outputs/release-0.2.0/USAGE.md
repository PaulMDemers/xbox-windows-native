# Using the private 0.2.0 HD release

This is an upgrade for the tested Conexant Xbox running the existing audio004/softwarevideo118/shared158/FATX0101 demo. It is not an installer for an arbitrary Xbox or for the original0.1.0 system. Read README.md and QUALIFICATION.json for evidence and known limitations. The console was restored to its working baseline after testing; this package has not been installed automatically.

## Choose a profile

Extract `xwn-0.2.0-hd-overlay.zip`. Its folders are:

| Folder | Use |
| --- | --- |
| `720p/E` and `720p/F` | 1280×720×32 output |
| `1080i/E` and `1080i/F` | 1920×1080×32 interlaced output |
| `baseline-restore/E` and `baseline-restore/F` | The six original files captured immediately before trial324 |

Both HD profiles reserve9MiB at physical55MiB, including hidden framebuffer storage. Install all six matching files together. Mixing an HD loader with the original4MiB boot/video chain is unsupported. Windows dynamic mode switching and GPU acceleration are not provided.

## Install on the qualified console

1. Shut down Windows normally and return to UnleashX. Keep a separate current backup. Use the tested HDTV-capable cable/adapter and enable the desired HD mode in the dashboard. A connector shaped like HDMI does not by itself establish HDTV support.
2. Verify the archive SHA256 against bundle.json or SHA256SUMS.txt. PowerShell example: `Get-FileHash .\xwn-0.2.0-hd-overlay.zip -Algorithm SHA256`. Compare the installed files with `installed_prerequisite_files` in MANIFEST.json. If the baseline differs, stop the upgrade and review that installation rather than assuming compatibility.
3. Choose **one** profile. With Windows stopped, upload its six files over dashboard FTP to these paths, replacing only those files:

   - `E:\Applications\XWNFBoot\default.xbe`
   - `E:\Applications\XWNFBoot\freeldr.sys`
   - `E:\Applications\XWNFBoot\rosload.exe`
   - `E:\Applications\XWNFBoot\loader\xboxbvid.dll`
   - `F:\winnt\system32\drivers\xboxvnt5.sys`
   - `F:\winnt\system32\xwnown.dll`

4. Download all six files again and compare their SHA256 values with that profile's entries in MANIFEST.json. Do this before booting. Leave normal startup and registry settings unchanged. This overlay requires no diagnostic autorun, EEPROM write or partition formatting. Dashboard `F:` maps to Windows `C:` on this installation.
5. Launch the root **Windows** menu entry in UnleashX. Keep the Razer keyboard unplugged through Xromwell, where it previously caused a hang; reconnect after Windows starts if needed.
6. Check the picture and display mode. Use Windows Start → Shut Down → Restart to return to the dashboard. Record any signal loss, abnormal picture or shutdown failure before another run.

## Restore the previous display profile

Return to UnleashX and upload the six files from `baseline-restore` to the same paths, then download/readback-verify them against MANIFEST.json. If Windows responds, restart it normally first. If it cannot be used, return through the console's normal dashboard boot path and record any forced reset separately. The dashboard's root Windows entry is unchanged.

The optional larger `xwn-0.2.0-private-demo.zip` also includes the original demo256 system and boot/dashboard recovery archives under `recovery/`. Their original manifest and exclusions are included. They were captured before the HD work and are broader historical recovery copies, **not a tested bare-metal restore procedure**. Restoring them may replace user files and configuration. Do not extract them indiscriminately over an existing installation; review paths and preserve current data first. Neither those archives nor this overlay include a whole disk, firmware, all applications/games or all console partitions.

## Known limits

The Ftdisk49 event remains a strict test failure. Unsupported-device dialogs may remain; exact stereo routing, repeated HD boot reliability and recovery from arbitrary power loss are unproven. This release supports the tested Conexant/HDTV configuration, not every encoder or adapter. Keep the package private: it contains owned binaries and the optional recovery archive contains system/user data.
