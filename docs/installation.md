# Installation and first boot

There are two different starting points. An already configured Xbox can use the
integrated demo now. A fresh Xbox still needs a qualified provisioning workflow;
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

That test used an already prepared private Windows payload, not an assembly
from a newcomer's Windows media. It does not qualify the FTP migration tool,
physical recovery or freshly compiled replacement drivers. Owned-media assembly
and reproducible registry/configuration provisioning remain the missing steps
for a general fresh installer. See [offline recovery](recovery-guide.md).

## Updating an existing installation

Use only a package explicitly naming your installation and prerequisite hashes.
Save work, return to the dashboard, preserve the exact previous bytes and verify
both upload and readback. Deploy the launcher last when an update needs one.
A compiler-success result alone is not hardware qualification. Keep rollback
separate and read [recovery](recovery-guide.md) before modifying the boot chain.
