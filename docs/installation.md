# Installation and first boot

There are two different starting points. An already configured Xbox can use the
integrated demo now. A clean-media assembly has also booted in an Xbox emulator,
but a fresh physical Xbox still needs a qualified provisioning workflow;
this repository does not yet offer a general Windows-from-CD/ISO installer.
Building the drivers alone does not create a bootable Windows installation.

## Already configured demo

1. Connect the mouse before boot. Keep a keyboard known to hang Xromwell
   disconnected until Windows appears; the Razer keyboard did so during testing.
2. In UnleashX, choose **Windows**. For the current E installation its executable
   is `E:\Applications\XWNEBoot\default.xbe`.
3. Windows should reach the desktop. Close unsupported-device wizards without
   disabling devices. These prompts are not evidence that all those devices
   have working drivers.
4. Use applications and save work on Windows C. Choose full-window or outline
   dragging using the supplied shortcuts; see [display settings](display-configuration.md).
5. Use Windows **Start → Shut Down → Restart** to return to the dashboard.

The normal demo has no benchmark or automatic timed restart enabled.

### Partition mapping on this E installation

| Dashboard namespace | Windows view/use |
|---|---|
| E | Windows C: system, applications and demo files |
| F | Original installation/rollback; preserve it |
| C | Dashboard/system files; appears as Windows F in this installation |

**Do not use Windows F as scratch.** It maps to the protected dashboard C here.
Do not assume these letters on a different console; verify its mapping first.
The host PC's C/E drives are unrelated to Xbox partition letters.

### Launch menu

If the menu starts an obsolete profile or a blank screen, first use UnleashX's
file explorer to inspect the intended E launcher. An authorized menu update
should change only the Windows item's launch action to the exact path above,
preserve the previous configuration and reload UnleashX. The old
`E:\Applications\XWNFBoot\default.xbe` selects a different Windows installation.
Do not replace dashboard configuration from another machine.

## Fresh Xbox: what is still required

The intended route uses dashboard E so it can support stock-size disks, with F
optional for additional storage/rollback. It needs:

- An Xbox able to run the launcher, a working dashboard and compatible display
  path; the tested console has 64 MiB and a Conexant encoder.
- Your own Windows installation materials and appropriately obtained firmware
  for any emulator testing. Neither is distributed here.
- The tested kernel/media baseline described in [provenance](provenance.md).
  Do not assume an arbitrary retail SP4 installation is interchangeable.
- A matched launcher/loader/HAL/driver set, prepared Windows registry and files,
  a verified partition layout and sufficient space.
- A recoverable dashboard, preserved console-specific data and verified backups.

The historical `tools/install-stock-e.py` stock-E migration tool is an
engineering tool for a same-console captured baseline. It is **not** a fresh
Windows installer. Its create-only guards, capacity checks, launcher-last
ordering and readback journal have host tests; its physical FTP migration path
has not received a new end-to-end qualification. It must not be used to overwrite
an occupied installation or to install someone else's private system archive.
It is excluded from the portable source review package because it depends on
private engineering fixtures.

Independent source/dependency retrieval and HAL/network/input provenance are
now checked. A separate offline test installed all 6,571 files of the prepared
private E baseline into a fresh standard 10 GB image, verified every file,
backed up E, deliberately damaged launcher bytes and restored E exactly. Both
ranges outside E remained unchanged. The restored system subsequently booted
in xemu, passed its scoped audio/graphics and filesystem checks, and restarted
normally. Ftdisk 49 still failed the strict event gate.

That restore test used an already prepared private Windows payload. It does not
qualify the FTP migration tool or physical recovery. A separate clean-media
assembly now exercises the newly compiled components, as described below.
See [offline recovery](recovery-guide.md).

### Validated clean-media route in the emulator

The customized SP4 disc identified in the [media guide](windows-media.md) was
installed onto a new blank PC virtual disk. That installation supplied the
Windows files and registry for a new standard-size Xbox image. No Windows tree,
user hive or installed-device registry was borrowed from the working Xbox demo.

The validated engineering sequence is:

1. Verify the exact disc hash, install Windows on a disposable PC virtual disk,
   complete setup, then boot with installation media detached and shut down.
2. Extract the installed files with a complete manifest. Keep the original NTFS
   disk. Record paths FATX cannot represent; do not silently rename or discard
   cryptographic or application state.
3. Build the matched components using the [build guide](building.md). Select the
   required Microsoft boot/input files from the same disc and record their
   cabinet/member hashes and versions.
4. On copies of the fresh registry, configure Xbox FATX/IDE, video and USB/HID
   boot services and map Xbox E to Windows C. Record each changed value and
   verify every other raw registry value unchanged. A PC HAL/storage registry
   cannot simply be copied onto an Xbox.
5. Assemble E on a disposable standard 10 GB Xbox image. Preserve factory root
   entries and the separate dashboard. Read back every installed file and audit
   the entire FATX allocation before booting.
6. Boot, log on with the installation's own credentials, and install the Xbox
   audio/network packages through Windows Plug and Play. Allow Windows to
   finish its software-audio device setup and restart before testing audio.
   Unsupported-device wizards may require cancellation; do not disable devices
   or suppress signing/event policies to make the test pass.
7. Check a subsequent boot: exact file persistence, display drawing, audio API
   completion, real network transfer and normal shutdown. Inspect the closed
   disk's files, allocation, registry and event deltas independently.

This sequence passed its core boot and device checks in xemu, including 720p,
audio playback API completion and 128 KiB of independently checked TCP data in
each direction. It uses the fresh component builds, not the previous demo
binaries. It remains an engineering procedure, not a portable installer command.

The lossless-transfer and strict-event gates still fail. Eight paths were not
representable by the current FATX writer, including long crypto/COM+ names and
non-ASCII shortcuts. The original disk preserves them. Ftdisk 49, first-boot
Plug and Play warnings and a final-boot kbdhid 1 warning are retained. The customized disc's typed DRM registry
decoding limitation also remains. These results do not qualify an arbitrary
SP4 disc, physical deployment, restore, DRM/DPAPI behavior or every Windows
feature. A public installer needs explicit handling of these limitations.

## Updating an existing installation

Use only a package explicitly naming your installation and prerequisite hashes.
Save work, return to the dashboard, preserve the exact previous bytes and verify
both upload and readback. Deploy the launcher last when an update needs one.
A compiler-success result alone is not hardware qualification. Keep rollback
separate and read [recovery](recovery-guide.md) before modifying the boot chain.
