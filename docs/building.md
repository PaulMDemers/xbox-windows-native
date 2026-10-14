# Build the components

The build command reconstructs one reviewed component tree from an upstream Git
cache plus `src/`, then builds its selected binaries. It does not create Windows
media, configure a registry, install drivers, flash firmware or contact a console.

## Requirements

- Linux or WSL, Python 3.10+, Git, Make and normal build utilities.
- An upstream Git cache containing the exact manifest base commit. Linked Git
  worktrees are supported.
- Recorded RosBE 2.2.1 for ReactOS profiles, or recorded GCC 12 for Xromwell.
  Tool hashes are checked against [components.json](../upstream/components.json).
- At least 20 GiB free on the output filesystem and WSL's Windows backing volume.
  This reserve is checked; it is not a build-size estimate.
- A fresh output directory outside the repository, cache and toolchain. Prefer
  WSL's Linux filesystem for compilation speed.

This guide assumes the pinned source and toolchains are already available. A
verified anonymous dependency-download/bootstrap path remains release work.
Recorded URLs are provenance references; do not substitute arbitrary latest
revisions when reproducing the baseline.

## Commands

From the repository root:

```sh
python3 tools/xwn.py list
python3 tools/xwn.py verify
```

Choose your own paths. `CACHE` is a Git repository with the required ReactOS
base; `ROSBE` is the extracted toolchain directory:

```sh
CACHE="$HOME/upstream/reactos"
ROSBE="$HOME/toolchains/RosBE-2.2.1"
OUT="$HOME/build/xwn-fatx-001"
python3 tools/xwn.py build --profile fatx --cache "$CACHE" --rosbe "$ROSBE" --output "$OUT"
```

For source reconstruction only, use `source` instead of `build` and omit
`--rosbe`. The full Git tree must match. Keep the source cache while using the
output because the workspace borrows its objects read-only.

Repeat with **fresh output directories** for `framebuffer`, `loader`, `display`
and `audio`. They are independent trees; do not combine their build directories
or build every component from one profile. For Xromwell:

```sh
python3 tools/xwn.py build --profile launcher --cache "$HOME/upstream/cromwell" --gcc12 /usr/bin/gcc-12 --output "$HOME/build/xwn-launcher-001"
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

`--allow-modified` permits edits to listed source files and records their new
identity. New paths/deletions/modes need manifest review. On shared machines,
wrap builds in the machine's build lease/scheduler; this portable command does
not acquire a machine-specific lock or alter the shared SDK.

## Display-preference utility

[settings.c](../src/utilities/display-settings/settings.c) is independent of the
six overlays. With RosBE's i686 compiler on PATH, its recorded command is:

```sh
i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin -Wno-misleading-indentation -Wl,--entry,_mainCRTStartup@0 -Wl,--subsystem,console:5.0 -o display-settings.exe src/utilities/display-settings/settings.c -lkernel32 -luser32 -ladvapi32
```

The indentation-warning exemption is inherited from this utility's recorded
build; it is not a general suppression policy.
