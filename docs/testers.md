# Xbox tester quick start

Start with the inventory kit. The private Windows delivery587 is a prepared
E/720p test package, with copying instructions and checksums; it has not yet
been qualified on another console and is not a public Windows download.
Use a package explicitly prepared for your test, not a developer's disk/recovery
archive. Builders should follow the [two-kit recipe](build-test-kits.md).
The [compatibility matrix](console-compatibility.md) explains which hardware
assumptions need review before the initial Windows boot.

## 1. Report your hardware

Use **utilities preview 421 or later**, with hardware-report schema 2. The older
417/417b utility can hang the Xbox while querying a documented hazardous PCI
address; do not run it. The corrected scanner skips those addresses and completed
on the development console (64 MiB, Conexant response, kernel 1.0.4034.1), saving a
report and returning to dashboard FTP. A later user-supplied 1.6 schema-2 report
[passed validation](../outputs/inventory630/REPORT.md), with an unidentified
encoder; its auto-return was not observed here. That inventory is not Windows
support. Additional-console Windows tests are currently deferred.
See the [421 evidence](../outputs/inventory-pci421/REPORT.md).

You need an original Xbox that already runs homebrew, a working dashboard with
FTP, and a PC on the same local network. This kit does not install a mod or flash
a BIOS. Keep your existing dashboard and recovery route working.

1. Extract the utilities ZIP on your PC. Do not upload the whole archive.
2. Verify it with Python 3.12+: `python host/tester_bundle.py verify PATH_TO_ZIP`.
   Compare the archive's SHA-256 with the maintainer's separately supplied value.
3. Copy the extracted `E/Applications/XWNInfo` folder by FTP to
   Xbox `E:\Applications\XWNInfo`. Stop if that folder already exists; keep the
   previous version and ask which version to use. Do not overwrite other Apps.
4. In UnleashX File Explorer, launch `E:\Applications\XWNInfo\default.xbe`.
5. The tool saves `E:\xwn-report-00.json` (or the next unused number), reads it
   back, displays a summary in 640×480 and requests a return to the dashboard
   after 20 seconds. Allow up to a minute. Report any error or failure to return.
6. FTP that JSON back to your PC. Run `python host/hardware_report.py xwn-report-00.json`.
   Send the JSON and the completed [test report](tester-report-template.md).

The tool reads kernel/PCI/video information and free space. Its only file write
is a new numbered JSON on dashboard E; it never overwrites an existing report.
It probes Conexant and Focus responses but **does not identify Xcalibur merely
because those probes failed**. Kernel-reported RAM and available video modes
are observations, not proof that Windows supports them.

No EEPROM contents, HDD keys, serial number, MAC address, firmware or Windows
registry are collected. Do not attach those separately. The library may perform
normal runtime initialization; this is a homebrew diagnostic, not a passive
electrical measurement. The PCI list contains raw responding locations, including
possible function aliases; its length is not a count of independent physical
devices. Policy `xbox-safe-v1` leaves hazardous 00:00.1/00:00.2 and bus-1 GPU
device aliases unprobed. Omitted addresses are not evidence of absent hardware.

## 2. Prepare for a Windows preview

- Back up your own dashboard E files, particularly Apps, TDATA and UDATA, using
  your established backup method. Keep recovery materials privately.
- Leave Xbox **C completely alone**. Do not format partitions, replace dashboard
  configuration, flash a BIOS or copy another console's keys.
- Tell us your known revision/encoder, RAM upgrade, BIOS/mod, cable/HDMI adapter,
  display, disk size and available E space. Unknown is a useful answer.
- The current preview target is **dashboard E with a matched 720p boot chain**.
  Moving it to F or renaming XWNEBoot does not select a different Windows root.
  F is optional, not a prerequisite.
- An unknown encoder or non-HD configuration needs a reviewed matching profile
  before a Windows test. Do not enable HD with an unsupported cable/display.

## 3. Install a reviewed Windows package

These steps apply after the maintainer reviews the package and hardware report
for an initial watched test, or verifies a locally assembled package from your own media.
Record new-console compatibility as untested until that test completes.
The repository alone does not include Windows.

1. Verify the ZIP and its separately supplied hash. Read its profile and known
   issues. Do not use a package marked incomplete or a private recovery capture.
2. Compare the package's uncompressed `E` size with dashboard E free space. Leave
   additional room for the pagefile and saved files; the package must state its
   required reserve. ZIP size is not the installed size.
3. Check that `E:\WINNT`, `E:\Documents and Settings`, `E:\Program Files` and
   `E:\Applications\XWNEBoot`, plus any packaged support root such as
   `E:\xwndemo372`, do not conflict with existing files. If they do,
   stop. Do not merge or overwrite an older Windows installation.
4. FTP only the package's `E` contents into dashboard E, preserving the exact
   structure. Keep `default.xbe` out of XWNEBoot until everything else has
   transferred and been downloaded back to the PC for hash verification.
5. Upload `E:\Applications\XWNEBoot\default.xbe` last and read it back too.
   Keep the verified PC package and your backup. No menu edit is needed.

Put downloaded files under a new PC folder with the same `E/` structure, including
empty directories. Verify before the final launcher upload:

```sh
python host/tester_bundle.py verify-tree windows-preview.zip --root readback --console-only --defer-launcher
```

After downloading the uploaded launcher into that same readback tree, repeat
without `--defer-launcher`. Do not launch until the complete check succeeds.
The readback folder should contain only this package's E files, not the rest of
your dashboard drive. These commands verify files you download; they do not FTP.

There is no general-purpose automatic FTP installer yet. Hash verification
checks bytes; it does not prove a correct registry, partition mapping or recovery.
See [installation](installation.md) for the evidence limits.

## 4. Boot and test

1. Connect the mouse before launch. Leave a keyboard that hangs Xromwell unplugged
   until Windows starts. Use UnleashX **File Explorer** to launch
   `E:\Applications\XWNEBoot\default.xbe`. Do not substitute the front-page
   Windows item or FTP SITE launch for this comparison.
2. Record what appears: Xbox logo, Xromwell, Windows boot screen, desktop, or an
   error. If it returns to the dashboard, report the route; do not loop retries.
3. Note Found New Hardware prompts and device names. Cancel unsupported-device
   prompts without disabling devices. Do not install random driver packs.
4. Check small text, menus, colors and full-window dragging. Save a Notepad file
   and Paint picture to Windows C, close/reopen them, and check their contents.
   In this profile Windows C maps to dashboard E. Do not write to Windows F;
   on the current layout it maps to dashboard C.
5. Check login sound or a supplied/owned audio clip. Note left/right output if
   known. For Media Player, try a window first, then fullscreen. The current demo
   drops some fullscreen frames; report what you see and hear.
6. Use Windows **Start → Shut Down → Restart**. Confirm return to UnleashX, then
   perform one further direct File Explorer boot and check your saved files.

If the screen freezes or input stops, record the last state before any forced
restart. Distinguish a power cycle from a normal Windows restart. Do not upload
Windows hives, keys or a disk image with the report.

## 5. Remove the preview

From the dashboard, remove only the exact new Windows/utility paths listed in
your package manifest, and only if they were absent before installation. Keep
documents you created. Do not delete all of E, Apps, TDATA or UDATA. If existing
files changed, restore your own verified backup, not someone else's dashboard.
A verified physical rollback is still a release gate.
