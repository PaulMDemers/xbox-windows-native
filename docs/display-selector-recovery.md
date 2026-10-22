# Explicit 480p and 720p boot selection

The experimental selector now accepts the qualified native 480p launcher.
720p remains the default and recovery profile. This changes the **next boot**;
it does not switch resolution inside Windows. The 480p desktop is **720x480x32**,
not 640x480. Original-console drawing and interaction passed trials 638 and 642;
the saved file was also reopened through ordinary 720p in 643. The newly extended
selector has host fault-injection coverage. [Trial645](../outputs/display-selector645/REPORT.md)
passed physical480p apply/readback and720p restoration, but the480p boot showed
black and returned without new Windows events. A successful selector boot cycle
is still pending. The frozen644 archive retains its original pre-test instructions;
it has not been repackaged or silently updated.
The restored720p recovery boot subsequently passed in
[646](../outputs/display-selector646/REPORT.md), including the watched desktop,
normal restart and selected-file/hive audit. Ftdisk49 remains.

Use this only with the matching existing E installation on the qualified original
Conexant console. The pinned 480p loader requires the HDTV AV-pack classification
and enabled 480p video flag, and refuses unsupported hardware rather than silently
falling back. The PC selector verifies file hashes, not live hardware identity.
It does not identify an HDMI adapter brand or query HDMI EDID. Focus/Xcalibur,
including Xbox 1.6, remain unqualified for this candidate.

## Build the small selector archive

Reconstruct the pinned launchers using the existing source/build records:
[720p build](../outputs/resolution-e374/build001.json) and
[480p build](../outputs/native480p633/build001.json). The latter uses source tree
`70c0a6c5aff82537f489e7d18410d5980fa797a7` and the explicit mode3 build flags in
that record. Use the [current build instructions](BUILD-CURRENT.md) in the source
checkout, plus the exact recorded patch order and compiler; a generic
current-tree build is not a substitute for these pinned artifacts.
These build-record links refer to the source repository, not files in the small ZIP.

From the source checkout, supply your locally retained/rebuilt matching files:

```powershell
python tools/package-e-display.py --launcher-480p PATH_TO_480P/default.xbe --launcher-720p PATH_TO_720P/default.xbe --output PATH_TO_NEW_ARCHIVE.zip
```

The packager rejects different binary hashes and an existing output archive. It
reads back every ZIP entry. The archive includes the two launchers, selector,
policy and instructions; no Windows, game, firmware or credentials. Older release
ZIPs are unchanged and do not gain 480p merely by selecting it in this new tool.
The source checkout contains no compiled launchers.

## Select 480p, then return to 720p

Extract the new archive on the PC. Save Windows work and return to UnleashX.
Set `XWN_FTP_HOST`, `XWN_FTP_USER` and `XWN_FTP_PASSWORD` in that process's
environment. Run from the extracted directory:

```powershell
python tools/configure-e-display.py inspect --policy tools/e-display-policy.json
```

For the first qualification, the result must say `720p`. Preserve this known-good
starting point. Apply the pinned low-resolution launcher with a fresh receipt:

```powershell
python tools/configure-e-display.py apply --policy tools/e-display-policy.json --profile 480p --launcher resolution/480p/default.xbe --receipt rollback-480p-001
```

Keep the receipt on the PC. It contains the exact prior launcher and hashes. The
tool checks all five prerequisite files, rechecks the installed launcher, writes
only `E:\Applications\XWNEBoot\default.xbe`, then verifies exact readback. It
does not launch Windows, change EEPROM flags or install a startup hook.

Launch the ordinary E Windows entry once. Check the desktop and interaction,
then use Windows Restart to return to UnleashX. Restore the captured 720p profile:

```powershell
python tools/configure-e-display.py restore --policy tools/e-display-policy.json --receipt rollback-480p-001
python tools/configure-e-display.py inspect --policy tools/e-display-policy.json
```

Confirm `720p` before launching again. Restore means **the captured prior mode**,
not always 720p; that is why this first test starts from a verified 720p profile.
Use a new receipt for every later change. Do not overwrite prior receipts or
repeat a launch whose outcome is uncertain.

## Interrupted transfer or blank boot

If a write or readback fails, the tool attempts to restore the captured launcher
and records whether that rollback was verified. A failed command is not success,
even if it subsequently restored the old bytes. Read the receipt's `result.json`.

If rollback also fails, keep the receipt and reconnect at UnleashX. A partial
launcher is deliberately rejected by `inspect`/`restore`; do not force it through
by editing the policy. Verify `before.xbe` against `intent.json` and the policy's
720p hash (for the sequence above), then use dashboard FTP to copy that exact file
to `E:\Applications\XWNEBoot\default.xbe`. Download it again and compare SHA-256
before launching. This manual recovery requires a reachable dashboard and has
not been physically fault-injected. Never write dashboard C or substitute an F
installation launcher. A blank boot may require a hardware reset to reach the
dashboard; the PC tool cannot recover an unreachable console.

1080i remains a separate, tabled diagnostic. Boot intermittency and Ftdisk49 remain
open. This selector does not qualify live mode switching, fullscreen applications,
other consoles, or acceleration.
