# Windows installation media

Use your own appropriately licensed Windows 2000 media. The project does not
include Windows, product keys or installed system images. A matching hash
identifies a disc; it does not grant a license or establish Microsoft authenticity.

## Identify your ISO

From the repository root, with Python 3:

```sh
python3 tools/verify-media.py --iso "/path/to/your/disc.iso"
```

The command reads the ISO without changing it and prints its size, SHA-256,
SHA-1 and the recorded validation scope from
[windows-media.json](../upstream/windows-media.json). Exit status 0 means an
exact recorded size/SHA-256 match; 2 means unknown media. A renamed ISO still
matches. Do not treat recognition as a successful installation test.

## Recorded discs

| Disc | Bytes | Kernel from disc | Installation channel |
|---|---:|---|---|
| `EN_WIN2000_PRO_SP4.ISO` | 386,859,008 | 5.0.2195.6717 | Retail |
| `Windows 2000 (SP4).iso` | 594,280,448 | 5.0.2195.7376 | Customized, OEM channel |

The retail disc's SHA-256 is:

```text
e3816f6e80b66ff686ead03eeafffe9daf020a5e4717b8bd4736b7c51733ba22
```

The customized disc's SHA-256 is:

```text
75ae5e4980e074377d3f0c2ab2e82dff0e3f80400da13c8e2d5a1479d2ccda1f
```

Both SHA-1 values and detailed results are in the manifest. The customized disc
contains additional setup content and later Windows files. It is not described
as an unmodified Microsoft SP4 release. The current Xbox demo's 7376 kernel and
6875 keyboard class originate from this customized baseline; the retail disc
is not an interchangeable source for those files.

The customized disc passed a new blank-disk PC installation, first logon and
subsequent media-detached desktop boot on October 15, 2026. Both shutdowns were
recorded; the installed 7376 kernel matched the disc. All five hive headers were
clean, and two independent readers agreed on every stored key/value. No warning
or error event records were found in the two cold audits.

This is a **scoped installation pass**, with two test limitations retained:

- Setup removed the witness's scheduled RunOnce entry. The second boot reached
  the desktop normally, then the witness was launched manually through Run.
  The fully unattended end-to-end harness did not pass.
- The Python typed registry decoder rejected `Microsoft\DRM\DataPath` type
  `0x404`. Independent raw-value comparison succeeded, but complete typed
  decoding remains failed. Its meaning was not inferred or rewritten.

The retail disc passed identity, file-read and selected cabinet checks. Its
fresh installation remains **pending a matching retail key**, not validated.

## Independent online comparisons

On October 15, 2026, complete downloads from the Archive.org
[retail item](https://archive.org/details/en_win2000_pro_sp4) and
[customized item](https://archive.org/details/windows-2000-sp-4) matched the
respective supplied ISOs in size, SHA-256 and SHA-1, including a second readback
of each downloaded file. These are third-party catalog matches, not Microsoft
signatures. An identical downloaded copy does not require a separate duplicate
installation to identify its bytes; installation evidence belongs to the exact
disc identity and the recorded test configuration.

A second [retail catalog item](https://archive.org/details/win_2000_professional_sp4_english_202605)
reported the same size/SHA-1; that extra copy was not downloaded or installed.
Other customized discs with different hashes remain unvalidated.

The Microsoft sources located in this review were an
[SP4 update rollup](https://www.catalog.update.microsoft.com/ScopedViewInline.aspx?updateid=52f48ac0-4159-4842-9113-c75f32c42e51)
and an [April 2010 security-update ISO](https://www.microsoft.com/en-us/download/details.aspx?id=17207).
Neither is a full Windows installation disc. No current Microsoft-hosted full
installation ISO was verified during this review.

## What a clean-media test proves

The test starts from a new blank 2 GiB virtual disk, with no backing image,
copied Windows tree or preexisting registry. It uses a private answer floppy,
an original small first-logon witness, 64 MiB RAM, a Pentium III CPU model,
legacy IDE and Cirrus display, and no network adapter. The witness records
setup completion, then requests normal shutdown. A subsequent disk-only boot
removes both the ISO and answer floppy and records another logon/shutdown.
Cold inspection checks the witness files, installed kernel version, five
registry hives, setup state and event records. Private keys, hives, screenshots
and installed binaries stay outside the public package.

To repeat the PC installation independently, use a new disposable virtual disk,
install from your matching licensed disc, complete setup and logon, then shut
down normally. Detach both installation and answer media before the next boot.
Record the exact ISO hash, VM configuration, installed kernel hash, setup logs,
shutdown evidence and remaining errors. This project's run used QEMU 10.2.1;
the witness and cold-read results do not qualify a different VM configuration
automatically. Do not reuse a preinstalled Windows image as evidence of a
clean-media installation.

The answer file uses `OemPreinstall=No`; optional customized OEM post-install
commands are not replayed. This is a defined test configuration, not a claim
to reproduce every vendor customization. The retail disc requires its own
matching retail key; an OEM-channel key is not a substitute.

These PC setup checks are separate from compiling the project's open-source
components. A subsequent fresh assembly from this exact customized-disc PC
installation booted on Xbox emulation using the newly compiled components and
explicit registry conversion. File persistence, 720p offscreen drawing, audio
API playback and exact bidirectional TCP transfer passed. No old Xbox Windows
tree or machine/user hive supplied that assembly.

Strict qualification remains false. The original assembly excluded eight paths;
follow-up native CP437 handling restored two floppy shortcuts, leaving **six
overlong paths unresolved**. Ftdisk 49, first-boot Plug and Play and final-boot
kbdhid 1 warnings remain, and the typed DRM decoder limitation is unchanged. See the
[installation procedure](installation.md#validated-clean-media-route-in-the-emulator)
and [validation](validation.md) for scope and outstanding physical/recovery
work. Do not copy the PC's HAL or storage configuration directly onto the Xbox.

For what happens after PC setup, continue with the
[Windows preparation and copying guide](build-to-boot.md#3-prepare-the-windows-tree-for-xbox).
It separates the original NTFS installation, the converted Xbox payload and the
final verified transfer; verifying an ISO alone does not perform those steps.
