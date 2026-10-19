WINDOWS 2000 FOR ORIGINAL XBOX — PRIVATE E/720p TEST COPY
Prepared October 19, 2026 for Paul's own consoles. RCT Deluxe is NOT included.

This is a complete file copy of the development Xbox's ordinary Windows
installation, matched modified drivers/DLLs, loader and Xromwell default.xbe.
It is a private experimental deployment, not a new Windows installer or a
general hardware-compatibility release. It retains the existing Windows profile
and licensing data. Keep this ZIP private; do not upload it as a public release.

START HERE
1. Unzip Xbox-Hardware-Info.zip on the PC. Copy its E/Applications/XWNInfo
   folder to the same location on each Xbox's dashboard E drive. Run
   E:\Applications\XWNInfo\default.xbe in UnleashX File Explorer. After it
   returns, FTP E:\xwn-report-00.json (or the next number) back to the PC.
   Keep each report in a folder named for that Xbox. The kit's README explains
   how to verify the report. The utility does not install Windows.
2. The Windows baseline is 64 MiB RAM, a Conexant encoder and working 720p
   component/HDMI output on a homebrew-capable Xbox. Other encoders, BIOSes,
   RAM upgrades and partition layouts have not been qualified. Send the
   hardware report first so the boot/display profile can be compared.
3. Back up the target Xbox's own E files. Leave dashboard C, TDATA, UDATA,
   firmware and EEPROM alone. No BIOS flash, formatting or dashboard edit is
   required. Never copy another console's keys or dashboard configuration.

VERIFY AND COPY WINDOWS
4. Verify the ZIP with Python 3.12 or newer:
     python host/tester_bundle.py verify PATH_TO_WINDOWS_ZIP
   Compare its SHA-256 with the separate .sha256 file. MANIFEST.json lists
   every installed file and empty directory. The support files and docs outside
   E stay on the PC.
5. Have at least 1.25 GiB free on dashboard E before copying. The Windows tree
   is about 676 MiB; the remaining space is for paging, logs and your saves.
   Stop if E:\winnt, E:\documents and settings, E:\program files,
   E:\Applications\XWNEBoot or E:\xwndemo372 already exist. Do not merge an
   older Windows installation. Preserve your own backup before changing it.
6. FTP the CONTENTS of this ZIP's E folder to dashboard E using binary transfer,
   preserving names, hidden files and empty directories. This creates:
     E:\winnt
     E:\documents and settings
     E:\program files
     E:\Applications\XWNEBoot
     E:\xwndemo372
   The last folder contains the normal startup display-settings dependency.
   Do not copy the E folder inside E, and do not upload the ZIP itself.
7. Upload E:\Applications\XWNEBoot\default.xbe LAST. Before uploading it,
   download the other installed files into a fresh PC readback/E directory:
     python host/tester_bundle.py verify-tree PATH_TO_WINDOWS_ZIP --root readback --console-only --defer-launcher
   Then upload and download default.xbe, and repeat without --defer-launcher.
   Keep the ZIP and your own backup. Do not start Windows after a failed check.

BOOT AND REPORT
8. For the first comparison, power off for about ten seconds, turn the Xbox on,
   and launch E:\Applications\XWNEBoot\default.xbe from UnleashX File Explorer.
   This is the Xromwell launcher; keep the folder name and E location intact.
   Connect the mouse before boot. If a keyboard hangs Xromwell, attach that
   keyboard after Windows starts. There is no timed benchmark or automatic
   test restart in this package.
9. Record Xromwell/Windows/desktop progress, image quality, input and prompts.
   Use a uniquely named Notepad file on Windows C, close/reopen it, then use
   Start -> Shut Down -> Restart. Confirm dashboard return and check the saved
   file on a subsequent boot. Keep each boot outcome separate in your report.
   On the source profile Windows C is dashboard E; Windows F is dashboard C.
   Do not write to Windows F. Confirm drive mapping on unfamiliar layouts.
10. Boot intermittency is unresolved: a launch can return black to the dashboard
    and a later manual attempt may work. A ten-second power-off is a useful
    workaround, not a guaranteed fix. Do not repeatedly reset during writes.
    Record any forced reset separately from a normal Windows Restart.

KNOWN LIMITS
- This exact ZIP has not yet completed installation/boot/removal on a second
  physical console. The source installation boots and runs Windows, but that
  does not qualify different hardware. Inventory first, then watched testing.
- Existing Ftdisk49 paging warnings and some shutdown/unsupported-device popup
  limitations remain. Clean-media FATX long-name limitations are unresolved.
- 720p is the working profile; do not substitute the separate 1080i experiments.
- No native GPU acceleration or game frame-rate result is claimed. Sound is
  deferred for this test. No RCT assets, media, saves or test launchers included.
- Only inactive .422used loader backups were excluded from the four captured
  installation roots. The active boot chain, registry and normal startup are
  unchanged. Pagefile.sys is generated at runtime and is not in the ZIP.

REMOVAL
From the dashboard, remove only the five new paths above, only if they were
absent before installation, and retain any documents you created. Do not remove
all of E or touch dashboard C. Restore your own backup if anything pre-existing
was changed. A different machine's recovery archive is not your rollback.

Send back: inventory JSON, console/model/mod/display notes, boot route/outcome,
normal restart versus reset, file-save result, and relevant screen photos.
Do not send Windows hives, product keys, EEPROMs or disk images with the report.
