# Using the private demo bundle

This bundle is for the existing owned E installation. It is not an empty-disk
Windows installer. Preserve the original F installation and your user files.
The complete private system archive contains Windows and user data and must not
be published. The smaller add-on archive also awaits source/license release review.

## On the configured console

1. Start UnleashX with the Razer keyboard unplugged through Xromwell boot.
2. Select **Windows** from the root menu. It should point to
   `E:\Applications\XWNEBoot\default.xbe`, the E installation.
3. Connect the keyboard after Windows appears. Close unsupported-device wizards
   without disabling devices, and close the Welcome window if it covers an app.
4. Use `C:\xwndemo372\Full window dragging.cmd` or `Outline dragging.cmd` to choose
   your preference. Changes apply immediately and persist for the current user.
5. Save files to Windows C, which is dashboard E. Restart through Windows when
   finished. Do not use Windows F as scratch; it maps to dashboard C here.

The working demo profile is720p. The user observed clean text and clean full
dragging at720p;1080i has an unresolved output problem and is retained for
diagnosis/rollback, not recommended as the demo profile.

## Applying the small add-on to this existing installation

Save work and return to UnleashX first. Preserve existing files before copying
`addon/xwndemo372` into dashboard `E:\xwndemo372`. The folder name stays372 even
though the included utility is corrected build376. Do not replace startup or
user profiles just to change dragging; use the command inside Windows instead.
The optional supplied startup applies outline once on a fresh installation;
later selections are retained. It is not necessary on the configured console.

Use the host tool in [DISPLAY.md](DISPLAY.md) to inspect/apply/restore resolution.
It requires the exact installed prerequisite hashes, backs up the current E
launcher and verifies every write. It never launches the console. Do not use
the older F overlay tools against the E installation.

## Menu and recovery

The installed menu repair changed only the root Windows item's Action. Its
original configuration is `C:\Dashboard\config.e380.bak`; the rest of dashboard C
remains out of scope. A fresh console needs its own reviewed menu configuration;
this archive intentionally contains no dashboard config, credentials or EEPROM.

Reload UnleashX after editing a menu entry. If needed, its file explorer can
launch the E executable directly. Keep the original F launcher
`E:\Applications\XWNFBoot\default.xbe` separate; it selects a different Windows
installation and is not the current demo entry.

If a mode loses video, return to UnleashX and use the selector's captured receipt
to restore the exact previous launcher. See [RECOVERY.md](RECOVERY.md). Archive
verification is not a successful full-system restore test, and extracting a
private archive over an occupied installation is not a supported upgrade.
