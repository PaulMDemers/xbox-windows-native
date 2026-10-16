# Build the components

The build command reconstructs one reviewed component tree from an upstream Git
cache plus `src/`, then builds its selected binaries. It does not create Windows
media, configure a registry, install drivers, flash firmware or contact a console.

Windows installation is a separate input. Use the [media guide](windows-media.md)
to check your ISO against the recorded disc hashes and installation results.

For the standalone inventory XBE, use the separate [nxdk utility build](tester-bundles.md#build-the-hardware-report-xbe).
It does not require Windows or the NT5 component toolchain.

## Requirements

- Linux or WSL, Python 3.12+ (including `tarfile.data_filter`), Git, Make and normal build utilities.
- An upstream Git cache containing the exact manifest base commit. Linked Git
  worktrees are supported.
- Recorded RosBE 2.2.1 for ReactOS profiles, or recorded GCC 12 for Xromwell.
  Tool hashes are checked against [components.json](../upstream/components.json).
- At least 20 GiB free on the output filesystem and WSL's Windows backing volume.
  This reserve is checked; it is not a build-size estimate.
- A fresh output directory outside the repository, cache and toolchain. Prefer
  WSL's Linux filesystem for compilation speed.

## Obtain the dependencies

Start with the host distribution's build tools: GCC/G++, binutils, GNU Make,
Texinfo (`makeinfo`), m4, bzip2, tar, pkg-config and zlib development headers.
`python` must resolve to Python 3; some distributions package that alias separately.
The bootstrap checks these prerequisites before creating its output. It does not
install system packages or change your default compiler. GCC 12 is additionally
required for the launcher; its currently accepted binary hash is in the manifest.

Use new directories for each command:

```sh
DEPS="$HOME/xwn-dependencies-001"
BOOTSTRAP="$HOME/xwn-rosbe-001"
python3 tools/setup-dependencies.py fetch --output "$DEPS"
python3 tools/setup-dependencies.py bootstrap --archive "$DEPS/RosBE-Unix-2.2.1.tar.bz2" --output "$BOOTSTRAP"
python3 tools/toolchain_receipt.py --bootstrap "$BOOTSTRAP/bootstrap.json" --output "$BOOTSTRAP/toolchain.json"
```

The fetch uses public URLs, exact Git commits and an SHA-256-pinned RosBE archive
from [dependencies.json](../upstream/dependencies.json). It disables Git credential
helpers and prompts. The bootstrap applies one checked compatibility change to
Ninja's Python quoting API, then compiles RosBE into its private prefix. Failed
attempts remain intact. A receipt inventories all resulting files and symlinks;
later builds refuse missing, extra or changed tools/libraries.

Receipts describe **your local build**, and are not publisher signatures or proof
of historical compiler identity. Create them yourself from the pinned inputs;
do not trust an arbitrary downloaded toolchain and receipt. Anonymous fetching,
a fresh RosBE bootstrap, all eight component builds and the settings utility
passed on the development host. The seven ReactOS profiles used that freshly
compiled toolchain. This was not a pristine operating-system image test; host
build prerequisites and the launcher's GCC 12 were already installed.

## Commands

From the repository root:

```sh
python3 tools/xwn.py list
python3 tools/xwn.py verify
```

Choose your own paths. `CACHE` is a Git repository with the required ReactOS
base; `ROSBE` is the extracted toolchain directory:

```sh
CACHE="$DEPS/reactos"
ROSBE="$BOOTSTRAP/RosBE-2.2.1"
OUT="$HOME/build/xwn-fatx-001"
python3 tools/xwn.py build --profile fatx --cache "$CACHE" --rosbe "$ROSBE" --toolchain-receipt "$BOOTSTRAP/toolchain.json" --output "$OUT"
```

For source reconstruction only, use `source` instead of `build` and omit
`--rosbe`. The full Git tree must match. Keep the source cache while using the
output because the workspace borrows its objects read-only.

Repeat with **fresh output directories** for `framebuffer`, `loader`, `display`
and `audio`, plus the separate `hal` and `network` profiles. They are independent trees; do not combine their build directories
or build every component from one profile. For Xromwell:

```sh
python3 tools/xwn.py build --profile launcher --cache "$DEPS/cromwell" --gcc12 /usr/bin/gcc-12 --output "$HOME/build/xwn-launcher-001"
```

This launcher selects E-partition 720p. Other resolutions need matched profiles
and validation, not a single changed compiler flag.

## Results

| File/directory | Meaning |
|---|---|
| `source/` | Detached base checkout with maintained overlay |
| `source.json` | Base/tree identity and explicit development edits |
| `build-command.json` | Command, tool pins and capacity checks |
| `build.log` | Compiler output, including warnings |
| `artifacts/` | Selected binaries under installation filenames |
| `build.json` | Artifact sizes/hashes and source/tool identities |

Failed attempts remain for inspection; use a new directory next time. Successful
compilation is not historical binary identity or hardware qualification. Follow
[development](development.md) and [installation](installation.md) before deployment.

### Comparing a rebuild with an installed binary

A different SHA-256 does not by itself show a code change. These builds can embed
PE timestamps and checksums, diagnostic source paths, and generated version/date
strings. Changes to string lengths can also move data and the instructions that
reference it. Compare the complete files with an explicit list of allowed
metadata fields; do not simply strip every differing byte or compare file sizes.

For the HAL and loaders, ReactOS's relative-filename macro depends on the source
root's length as well as its spelling. A compiler prefix map alone may therefore
leave different references. FreeLoader also embeds a generated build banner
whose date and revision depend on the build environment.

The [loader correspondence experiment](../outputs/loader-correspondence416/REPORT.md)
rebuilt the HAL, FreeLoader and ROS loader with the independently bootstrapped
toolchain. Matching the recorded source-path spelling/length and, for FreeLoader,
the original generated version header produced complete-file matches outside
timestamps and checksums. The ordinary build command still records its actual
date/revision; it does not silently impersonate the historical build. The
experiment's frozen banner is a reconstruction control, not a new release label.
This result establishes source/compiler correspondence, not a fresh installation
or hardware qualification of every new build.

Keep the build receipts and original source identity alongside any normalized
comparison. Report unexplained differences and retain unsuccessful comparisons.

`--allow-modified` permits edits to listed source files and records their new
identity. New paths/deletions/modes need manifest review. On shared machines,
wrap builds in the machine's build lease/scheduler; this portable command does
not acquire a machine-specific lock or alter the shared SDK.

## Display-preference utility

[settings.c](../src/utilities/display-settings/settings.c) is independent of the
eight profiles. With RosBE's i686 compiler on PATH, its recorded command is:

```sh
i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin -Wno-misleading-indentation -Wl,--entry,_mainCRTStartup@0 -Wl,--subsystem,console:5.0 -o display-settings.exe src/utilities/display-settings/settings.c -lkernel32 -luser32 -ladvapi32
```

The indentation-warning exemption is inherited from this utility's recorded
build; it is not a general suppression policy.
