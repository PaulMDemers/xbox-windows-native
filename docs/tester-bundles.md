# Tester bundles and local assembly

| Package | Contents | Readiness |
|---|---|---|
| Utilities | Hardware-report XBE, host validators, source/notices and instructions | Corrected 421 utility passed emulator and first development-console inventory; other revisions unqualified |
| Windows E/720p preview | Matched boot chain, prepared Windows files/registry and manifest | Not yet approved for general tester distribution |

Windows, firmware, EEPROMs, dashboards and console-specific recovery material
are not included in the public utility package. Build Windows inputs locally
from your own installation materials. The ZIP tool does not convert an ISO,
fix the six outstanding FATX exclusions, sanitize a used system or establish
redistribution rights. See [media](windows-media.md) and [release gates](PUBLIC-RELEASE.md).

If you have component binaries but no prepared Windows tree, start with
[build to boot](build-to-boot.md). Packaging starts after Windows preparation;
it does not replace setup or the Xbox registry conversion. The same guide gives
the exact FTP destination and launcher-last readback steps.

## Verify an archive

From the repository root, using Python 3.12 or newer:

```sh
python tools/tester_bundle.py verify path/to/xwn-utilities-preview.zip
```

The bundle contains the same command under `host/`, so testers need not clone
the repository. It rejects missing, changed, extra, duplicate and unsafe entries.
The manifest is not a signature: compare the ZIP's SHA-256 with a value obtained
separately from the maintainer.

To verify an extracted PC tree, use `verify-tree ARCHIVE --root EXTRACTED`.
For manually downloaded console files, add `--console-only` and retain the `E/`
directory structure. `--defer-launcher` checks a Windows transfer before the final
XBE is uploaded; omit that option for the final complete readback. No transfers
are performed by these commands.

## Build a local package

Create a new staging directory. Its `E/` folder represents dashboard E.
`docs/`, `host/`, `source/` and `licenses/` stay on the PC; do not FTP them.

```text
staging/
  E/Applications/XWNInfo/default.xbe
  docs/
  host/
  source/
  licenses/
```

Plan, inspect, then build with fresh output names outside staging:

```sh
python tools/tester_bundle.py plan --kind utilities --root staging --output utilities-plan.json
python tools/tester_bundle.py build --root staging --manifest utilities-plan.json --output utilities.zip
python tools/tester_bundle.py verify utilities.zip
```

Every file must still match the plan. The archive is read back and hashed after
writing. Fixed entry timestamps produce identical ZIPs for identical contents
on the same Python/zlib implementation. Failed partial outputs remain for diagnosis.

For a **private, prepared Windows tree**, use `--kind windows-e-preview` when
planning and `--private-windows` when building. Allowed console roots are
`E/WINNT`, `E/Documents and Settings`, `E/Program Files` and
`E/Applications/XWNEBoot`, plus `E/xwndemo372` for the existing normal-startup
display-settings dependency. Do not omit a support path referenced by the
packaged startup scripts. Essential filenames, lossless OEM437 FATX names and
collisions are checked; this does not prove those files form a working OS.
Every manifest retains `experimental-not-hardware-qualified` status. No command
connects to or launches a console.

The [private delivery587 record](../outputs/delivery587/README.md) documents a
complete development-console E/720p snapshot, its source/ZIP integrity checks
and the existing startup dependency. Its [copying instructions](../outputs/delivery587/WINDOWS-README.txt)
cover inventory first, 1.25 GiB target E headroom, separate extraction folders,
binary FTP, uploading the launcher last, round-trip verification and removal.
The two private ZIPs exclude RCT and have no public download. Successful
packaging does not qualify installation or boot on another Xbox.

## Build the hardware-report XBE

Source: [src/utilities/hardware-report](../src/utilities/hardware-report).
Use [nxdk](https://github.com/XboxDev/nxdk) revision
`58427c078b4ccb0121f359b6b6c536b3b2914976`, including its pinned submodules
and nxdk's documented prerequisites. Runtime libraries must be built for that
revision. The recorded 421 build used prebuilt SDK libraries; it is not a clean
rebuild of the SDK itself.

In a configured nxdk shell, copy the source to a fresh, short build path:

```sh
mkdir -p /path/to/new-hardware-report-build
cp src/utilities/hardware-report/main.c src/utilities/hardware-report/pci_probe.h src/utilities/hardware-report/Makefile /path/to/new-hardware-report-build/
cd /path/to/new-hardware-report-build
make NXDK_DIR=/absolute/path/to/nxdk V=1
```

Results: `bin/default.xbe` and `hardware-report.iso`. The XBE goes in the FTP
utility bundle; the ISO is for a separate owned emulator fixture. Do not flash
either file. Preserve the compiler log and source/SDK hashes. Check recursive
clean rules before running `make clean` against a shared SDK.

The tested build has one inherited SDK linker merge warning and no native C
warnings. The tool checks or creates the E drive alias only for
`\Device\Harddisk0\Partition1`, refusing a conflicting mapping. It does not
change partition tables or dashboard settings. The schema-2 scanner excludes
documented hazardous PCI locations and GPU device aliases. Do not distribute the
older 417/417b binary. See [421](../outputs/inventory-pci421/REPORT.md) for exact
build, emulator and development-console results; other revisions are unqualified.
