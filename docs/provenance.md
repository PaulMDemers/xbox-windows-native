# Where the components come from

This project supplies an Xbox boot/platform adaptation and drivers. It does not
replace or redistribute Windows. Building the open-source components still
requires a separately prepared, appropriately licensed Windows installation.

The tested Windows kernel is **5.0.2195.7376**, from the supplied customized
OEM-channel media. Its
current package hash matches the original installed-media audit. This is a
specific compatibility baseline, not a claim that every retail SP4 kernel is
interchangeable with the Xbox HAL. The kernel hash is also recorded below.

Full-disc identities, independent online comparisons and clean-media setup
results are recorded in the [Windows media guide](windows-media.md) and its
machine-readable manifest. Neither matching filenames nor the label "SP4"
establishes that two discs contain the same Windows files.

| Component | Source/build profile | Current correspondence |
|---|---|---|
| Xromwell E launcher | `src/boot/xromwell`, `launcher` | Separate Cromwell base and flags |
| FreeLdr/ROS loader | `src/boot/loader`, `loader` | Pinned independent ReactOS tree |
| Xbox HAL | `src/platform/nt5`, `hal` | Reconstructed code/data matches; only timestamp/checksum fields differ |
| NVNet Ethernet | `src/platform/nt5`, `network` | Reconstructed code/data matches; only timestamp/checksum fields differ |
| FATX | `src/drivers/fatx`, `fatx` | Maintained current enumeration fixes |
| Framebuffer miniport/boot drawing | `src/drivers/video/framebuffer`, `framebuffer` | Separate framebuffer reservation profile |
| Software GDI display | `src/drivers/video/display`, `display` | Software rendering; no native GPU acceleration |
| AC'97 audio | `src/drivers/audio`, `audio` | Preserved sample/upstream notices and support sources |
| USB, keyboard and mouse stack | User's Windows media | Microsoft components; excluded from project distribution |

The manifest records full tree identities, not only patch filenames. Some
profiles contain different versions of the same upstream paths. Build them
separately; do not combine overlays and assume the resulting tree is qualified.
Compilation, correspondence with an installed binary, and runtime validation
are separate results.

The HAL comparison used the historical compiler and reproduced both its source
path spelling and length. ReactOS embeds source-file strings and derives an
offset into them from the source-root length; changing only the spelling with
a compiler prefix map was insufficient. With both reproduced, every byte other
than COFF/export timestamps and the PE checksum matched. The network comparison
has the same metadata-only difference. These comparisons establish source
correspondence, not permission to substitute a newly compiled binary without
runtime validation.

## Windows input dependencies

The twelve checked dependencies are `openhci.sys`, `usbd.sys`, `usbhub.sys`,
`hidusb.sys`, `hidclass.sys`, `hidparse.sys`, `kbdhid.sys`, `mouhid.sys`,
`kbdclass.sys`, `mouclass.sys`, `hid.dll` and `pid.dll`. Each installed file was
compared byte-for-byte with the supplied Windows media. Their hashes and
classification are in [runtime-provenance.json](../upstream/runtime-provenance.json).

The tested `kbdclass.sys` is version 5.0.2195.6875 from the supplied OEM media.
It does **not** match the older copy in the supplied retail SP4 disc. Other
matches may be in `SP4.CAB` rather than the individual compressed I386 file or
`DRIVER.CAB`. This is evidence for the current demo's dependencies, not a claim
that arbitrary Windows 2000 discs yield the same installation. Do not download
replacement system DLLs from unofficial binary sites or redistribute these files
under the project's MIT license.

## What a public package may contain

Maintained source, build/configuration tools, preserved upstream licenses,
documentation and reviewed project-built components can be considered for the
release export. Windows media/components, product keys, firmware, EEPROMs,
dashboard files, user registries and private installation/recovery archives stay
outside it. The private development history and its local paths are not the
public source tree. See [licensing](licensing.md).
