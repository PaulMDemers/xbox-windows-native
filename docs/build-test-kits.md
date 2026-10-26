# Build the two Xbox test ZIPs

This is the assembly recipe for a standalone hardware-info kit and a private
Windows E/720p kit. The [587 delivery record](../outputs/delivery587/README.md)
records the example that was actually packaged and verified. Its Windows files
came from the stopped development installation, not a new installation from an
ISO. Neither ZIP contains RCT.
Additional-console testing is currently deferred; the procedure below documents
how to prepare and verify a future test, without qualifying another unit.

Commands below use Bash on Linux/WSL, Python 3.12+, and run from this repository's
root. Use a short, new private working directory outside the repository. Keep
the source checkout revision, tool versions, component receipts and final ZIP
hashes with each build. Do not run historical scripts under `outputs/` as a
portable installer: their paths and attempt IDs belong to recorded experiments.
Stop on any failed command; inspect its error and keep the failed attempt
instead of continuing with a partial stage or overwriting its outputs.

## 1. Obtain the inputs

| Input | How to obtain it | What it proves |
| --- | --- | --- |
| Hardware-info `default.xbe` | Follow the [pinned nxdk build](tester-bundles.md#build-the-hardware-report-xbe) | A newly compiled standalone scanner; qualify its output separately |
| Windows boot/driver components | Follow [building](building.md), then the [ten-file destination table](build-to-boot.md#1-collect-the-complete-component-set) | Compiled components, not an installed OS |
| Prepared Windows E tree | Use your own reviewed, stopped Xbox installation or an already prepared private package | A specific installation, with its own profile, registry and boot configuration |
| Windows from an ISO instead | Follow [setup and offline conversion](build-to-boot.md#2-install-windows-from-your-own-media) | An engineering route with unresolved conversion/long-name limitations |
| Source and notices | Project sources plus the exact SDK/component sources, revisions and notices used | Build provenance; see [licensing](licensing.md) |

The clean-media route still lacks a portable registry converter and a lossless
solution for six FATX-incompatible names in the tested installation. Building
the DLLs does not complete that stage. Do not copy an ordinary PC SYSTEM hive
to Xbox, omit those files, or claim these packaging commands fix the problem.

For the hardware kit, `SDK_EXPORT` below means a source-only export of the
actual nxdk checkout and its submodules, with their copyright/license files.
Record `git rev-parse HEAD` and `git submodule status --recursive` from that SDK.
Do not include `.git`, credentials or unrelated build products. The supplied
421 kit includes its reviewed SDK export; it can be retained for the same pinned
SDK inputs after verifying that kit. A different SDK build needs its own source
and notices. The project license does not replace SDK licenses.

## 2. Stage the hardware-info kit

Set the three input paths to the outputs you actually built/exported. None is
a path to a historical private experiment. Do not change a shared SDK to match
these examples; use the pinned setup described in the build guide.

```sh
KIT_ROOT="$HOME/xwn-test-kits-001"
INFO_BUILD="/absolute/path/to/new-hardware-report-build"
SDK_EXPORT="/absolute/path/to/reviewed-nxdk-source-export"

# mkdir deliberately fails if this work directory already exists.
mkdir "$KIT_ROOT"
U="$KIT_ROOT/hardware-stage"
mkdir -p "$U/E/Applications/XWNInfo" "$U/host" "$U/docs" \
    "$U/source/hardware-report" "$U/source/nxdk" "$U/licenses"
cp "$INFO_BUILD/bin/default.xbe" "$U/E/Applications/XWNInfo/default.xbe"
cp src/utilities/hardware-report/main.c src/utilities/hardware-report/pci_probe.h \
    src/utilities/hardware-report/Makefile "$U/source/hardware-report/"
cp -a "$SDK_EXPORT/." "$U/source/nxdk/"
cp tools/tester_bundle.py tools/fatx_names.py tools/hardware_report.py "$U/host/"
cp docs/testers.md docs/tester-report-template.md "$U/docs/"
cp LICENSE NOTICE.md "$U/licenses/"
cp -a LICENSES/. "$U/licenses/"
```

Before packaging, compare the staged C/header/Makefile with the frozen build
inputs. Record the XBE hash, compiler/SDK identities and build log under
`source/`. A receipt describes your build; do not copy an older build's success
claim onto a new executable. Keep the SDK's license files in its source export.

Write `hardware-stage/README.txt` with these tester steps:

1. Verify the ZIP and its separately supplied SHA-256 on the PC.
2. FTP only `E/Applications/XWNInfo` to dashboard `E:\Applications\XWNInfo`;
   stop if that folder already exists.
3. Launch `E:\Applications\XWNInfo\default.xbe` through UnleashX File Explorer.
4. After dashboard return, retrieve the next numbered `E:\xwn-report-*.json`.
5. Run `python host/hardware_report.py REPORT.json` and retain the report with
   that console's model/mod/display notes. A complete current report uses schema 2.

The scanner is independent of Windows. The XBE goes into this ZIP; the generated
`hardware-report.iso` does not. Do not include firmware, EEPROMs or Windows files.
If copying Markdown guides with repository-relative links, keep a link to their
repository versions in README so readers can open references outside the ZIP.

Build and verify, with the plan and ZIP outside the staging directory:

```sh
python3 tools/tester_bundle.py plan --kind utilities \
    --root "$U" --output "$KIT_ROOT/hardware-plan.json"
# Review the plan, including every console path, before continuing.
python3 tools/tester_bundle.py build --root "$U" \
    --manifest "$KIT_ROOT/hardware-plan.json" \
    --output "$KIT_ROOT/Xbox-Hardware-Info.zip"
python3 tools/tester_bundle.py verify "$KIT_ROOT/Xbox-Hardware-Info.zip"
python3 tools/tester_bundle.py verify-tree "$KIT_ROOT/Xbox-Hardware-Info.zip" \
    --root "$U"
```

## 3. Obtain a consistent Windows snapshot

For the existing E/720p installation, restart Windows normally to UnleashX
before downloading. Leave the console at the dashboard throughout the capture.
Download in binary mode, including hidden files and empty directories, into a
new private `snapshot/E/` tree. Do not download all of dashboard E into staging.

| Dashboard path | Required contents |
| --- | --- |
| `E:\WINNT` | Complete Windows files, modified DLLs/drivers and registry |
| `E:\Documents and Settings` | Profiles and normal startup files |
| `E:\Program Files` | This Windows installation's required application files |
| `E:\Applications\XWNEBoot` | Matched Xromwell XBE, both loaders, loader directory and configuration |
| `E:\xwndemo372` | For delivery587's startup: `display-settings.exe` and `outline-applied.txt` |

Names/capitalization should match the captured source. Inspect normal startup
scripts and registry startup entries for other dependencies or test hooks.
Delivery587's `xwnsetup.cmd` invokes `C:\xwndemo372\display-settings.exe`; Windows
C maps to dashboard E in that installation. The marker is part of its existing
configuration. Copy both exact files from that same installation rather than
inventing the marker or rewriting startup to avoid the dependency.

Capture twice into separate PC trees while Windows is stopped, compare complete
path/size/SHA-256 manifests, and investigate differences before packaging. The
bundle planner can create those manifests for each curated `E/` tree. An
already verified private ZIP may instead supply the prepared tree: verify it,
extract separately, and copy only its E tree into the new stage. Preserve its
original manifest and hash outside staging as provenance.

Keep the complete capture privately. Record any exclusions explicitly.
Delivery587 omitted only two inactive `.422used` loader backups from its four
installation roots, retained them privately, and added the two startup support
files. It did not rebuild or replace active components. For a newly compiled
component set, first qualify the matched overlay and registry on an owned test
installation; taking one DLL from a new build and the rest from an old ZIP is
not a validated rebuild.

Do not include `pagefile.sys`, RCT/media/saves, temporary test kits, dashboard C,
BIOSes, EEPROMs or another console's recovery material. The four installation
roots can themselves contain user software/data: inspect them, not just their
folder names. This is still a private Windows/profile/licensing snapshot; the
packager is not a privacy scrubber. Required names must pass FATX checks without
renaming or silent omission.

## 4. Stage and build the Windows kit

```sh
SNAPSHOT="/absolute/path/to/reviewed-snapshot"
W="$KIT_ROOT/windows-stage"
mkdir "$W"
cp -a "$SNAPSHOT/E" "$W/E"
mkdir -p "$W/host" "$W/docs" "$W/source" "$W/licenses"
cp tools/tester_bundle.py tools/fatx_names.py "$W/host/"
cp docs/installation.md docs/display-configuration.md \
    docs/tester-report-template.md docs/licensing.md "$W/docs/"
cp LICENSE NOTICE.md "$W/licenses/"
cp -a LICENSES/. "$W/licenses/"
```

Retain component build receipts and corresponding source identities under
`source/`. Include the display-settings source if that dependency is present.
Keep proprietary Windows inputs private. Write `windows-stage/README.txt` for
the actual package: use the [587 copying instructions](../outputs/delivery587/WINDOWS-README.txt)
as a worked example, updating its date, source profile, dependencies, file size,
tested hardware and known limitations. Do not inherit its claims for another build.

For the 587 tree, installed E files total 707763829 bytes; its instructions
require at least 1.25 GiB free on target E for files, paging and growth. For a
different tree, calculate its installed size and required runtime reserve again.
The host also needs room for staging, the ZIP and readback. Check the volume
holding WSL's backing VHD as well as the apparent Linux free space.

```sh
python3 tools/tester_bundle.py plan --kind windows-e-preview \
    --root "$W" --output "$KIT_ROOT/windows-plan.json"
# Inspect all files, required startup dependencies and exclusions.
python3 tools/tester_bundle.py build --root "$W" \
    --manifest "$KIT_ROOT/windows-plan.json" \
    --output "$KIT_ROOT/Windows-2000-Xbox-E720p.zip" --private-windows
python3 tools/tester_bundle.py verify "$KIT_ROOT/Windows-2000-Xbox-E720p.zip"
python3 tools/tester_bundle.py verify-tree "$KIT_ROOT/Windows-2000-Xbox-E720p.zip" \
    --root "$W"
```

The planner rejects unsupported roots, unrepresentable names, case collisions
and links/reparse points. It records every file and empty directory. The builder
refuses changed staged bytes and reads back the ZIP. This does not verify hive
semantics or prove bootability: retain independent hive checks, boot evidence
and the exact scope of any failures with the package.

## 5. Deliver, verify the copy, and test another console

Create sidecars from the final archives, without changing the ZIPs afterward:

```sh
(
    cd "$KIT_ROOT" || exit 1
    sha256sum Xbox-Hardware-Info.zip > Xbox-Hardware-Info.zip.sha256
    sha256sum Windows-2000-Xbox-E720p.zip > Windows-2000-Xbox-E720p.zip.sha256
)
```

Copy both ZIPs, sidecars and a short START-HERE.txt to the delivery drive. Hash
the copies on that drive and compare with the originals. On Windows, use
`Get-FileHash -Algorithm SHA256 PATH_TO_ZIP`. Extract the kits into separate PC
folders so their host tools and documentation do not overwrite each other.

Run inventory on the target first. Then follow [launcher-last FTP and readback](build-to-boot.md#5-copy-to-dashboard-e-then-read-it-back).
Copy only E contents, preserve the target's backups, and leave dashboard C alone.
Check collisions with all five packaged roots, including `xwndemo372` when used.
No BIOS flash or dashboard menu replacement is part of this workflow.

For the first watched test, record the inventory JSON and package hash, cold
start to the dashboard, then launch the exact XWNEBoot path. Record Xromwell,
Windows startup, desktop, display and input. Save a uniquely named Notepad file
on Windows C, close/reopen it, restart normally to the dashboard, and check the
same file after another boot. Separate each failed boot or forced reset from
normal restart evidence. Use the [report template](tester-report-template.md).
Sound and RCT are not part of this initial package check.

Only after a verified removable-drive copy exists should local delivery ZIPs
be candidates for space recovery. Keep their hashes, instructions and build
records. This does not authorize deleting source inputs, backing-chain parents,
disk evidence or private recovery archives. Packaging success, byte-identical
rebuilds and boot compatibility are separate results.
