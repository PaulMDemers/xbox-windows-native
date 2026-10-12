# HD upgrade staging bundle — not the0.2.0 release

This private bundle targets the existing audio004/softwarevideo118/shared158/FATX0101 Xbox Windows2000 demo. It is an upgrade overlay, not a Windows installer or a substitute for the full private recovery archives listed in MANIFEST.json. Do not apply it directly to the immutable0.1.0 installation.

720p passed its watched physical test. The1080i automated hardware workload has a separate evidence record; TV appearance/field-quality confirmation is required before0.2.0 is tagged. Read QUALIFICATION.json for the exact current scope. The console was restored after testing; creating this archive does not install it.

## Contents

| Folder | Purpose |
| --- | --- |
| `720p/E` and `720p/F` | Six matched files for1280×720×32 |
| `1080i/E` and `1080i/F` | Six matched files for1920×1080×32 |
| `baseline-restore/E` and `baseline-restore/F` | The six working files captured immediately before the1080i trial |

Both HD profiles reserve9MiB at physical55MiB, including hidden framebuffer storage. Their bootloader, boot video and display provider must be installed together. Do not mix a new loader with the original4MiB chain. Resolution is selected before boot; Windows mode switching and GPU drawing acceleration are not supplied.

## Use on this qualified console

1. Stop Windows normally and return to UnleashX. Use a supported HDTV/component-capable connection and enable the desired HD mode in the dashboard. This work covers the tested Conexant console and its detected HDTV AV pack; other encoder revisions, ordinary composite cables and arbitrary HDMI adapters are not qualified.
2. Keep a separate current backup. Verify the bundle SHA256 and per-file hashes in MANIFEST.json. Confirm the installed baseline matches the prerequisite hashes before replacing anything; a different deployment needs its own integration review.
3. Choose exactly one profile. With Windows stopped, upload its six files to the corresponding dashboard paths, overwriting only those files:

   - `E:\Applications\XWNFBoot\default.xbe`
   - `E:\Applications\XWNFBoot\freeldr.sys`
   - `E:\Applications\XWNFBoot\rosload.exe`
   - `E:\Applications\XWNFBoot\loader\xboxbvid.dll`
   - `F:\winnt\system32\drivers\xboxvnt5.sys`
   - `F:\winnt\system32\xwnown.dll`

4. Download/read back all six files and compare their hashes before booting. Keep normal startup unchanged; no registry edit, diagnostic autorun, partition format or EEPROM write is part of this overlay. Dashboard `F:` is this installation's Windows `C:`.
5. Launch the existing root **Windows** entry in UnleashX. Keep the Razer keyboard unplugged through Xromwell, where it has previously caused a hang. Reconnect only after Windows starts if needed.
6. Check the desktop, screen edges, text, colors, signal stability and TV mode report. Use Windows Start → Shut Down → Restart when finished. A stable picture and normal restart are required; do not infer them from a successful FTP transfer.

## Recovery and limits

At UnleashX, upload and read back the same six paths from `baseline-restore`. If Windows remains responsive, restart it normally first. If it cannot be used, return the console to its normal dashboard boot path; record any forced reset separately. The full demo256 system/boot archives remain the broader recovery copies, with hashes in the manifest. They were readback-verified, not full-restore tested or whole-disk images. No new full-system capture is included here.

The known Ftdisk49 event is retained and strict event qualification remains false. Unsupported-device prompts may remain. These tests do not establish hardware stereo routing, accelerated window dragging, universal encoder support, or arbitrary power-loss recovery. No test helper is enabled by this archive. Keep these proprietary/private binaries and recovery material out of a public source release.
