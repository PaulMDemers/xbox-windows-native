# Source reconstruction and build boundaries

Requirements for reconstruction: Python 3.11+, Git, a local trusted Git cache
containing the exact base commit, a fresh destination and at least 20 GiB free.
The source URL recorded during development is in components.json. Its current
public availability has not been checked. No tool downloads code automatically.

For example, from this package in Linux/WSL:

```sh
python3 -B tools/reconstruct.py --component fatx390 \
  --source-cache /path/to/reactos-cache --output /path/to/new-fatx-source
```

Choose `fatx390`, `hd300`, `boot-e334`, `display303`, `launcher-e720p374` or
`audio004`. Each destination must be new. Failures are retained; never reuse a
failed output. `--index-only` checks the exact tree without checking out files.
The tool copies Git objects into an independent repository, applies the pinned
patch and compares the full tree identity. It does not use shared alternates or
`git archive`, whose export-ignore handling would omit required tracked files.

## Compilation

components.json records the original definitions and targets for each component,
plus selected RosBE 2.2.1 tool hashes and the launcher compiler hash. These are
build inputs, not a fully provisioned toolchain lock. Compiler support files,
host libraries, timestamps and version-generation behavior still need closure.

In the matching RosBE i386 environment, configure each reconstructed ReactOS tree
in a separate new build directory with `toolchain-gcc.cmake`, the exact component
definitions and the listed targets. Do not reuse one component's CMake cache for
another. Audio builds both ac97xnt5 and ac97; only ac97xnt5 is the native demo
driver, renamed xwnaci207.sys without changing bytes. The launcher uses the
recorded GCC 12 hash, make target and flags; its version identity and linker-map
arguments still need a portable build wrapper. Its upstream build can generate
firmware outputs as well as an XBE; nothing here authorizes flashing those outputs.

Source replay has been tested; this export has not compiled the six-component
stack twice or booted rebuilt outputs. Matching a source tree is not proof of
matching a binary. The FATX patch is reconstructed from the tested390 tree;
the exported audio tree matches 32 compiled audio source blobs exactly. The
remaining ac97.inf matches its compiled-source hash after the upstream tree's
explicit `text eol=crlf` checkout rule. Both byte hashes and that rule are recorded
in components.json; the Git tree itself is not normalized or rewritten.
Historical build tests and the installed demo remain distinct from this export.

## Display preference utility

tools/display-settings.c is the current MIT preference utility. Its existing
build used the RosBE i686-w64-mingw32-gcc pin with:

```sh
i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib \
  -fno-stack-protector -fno-builtin -Wno-misleading-indentation \
  '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' \
  -o display-settings.exe tools/display-settings.c -lkernel32 -luser32 -ladvapi32
```

The inherited misleading-indentation warning exclusion is explicit, not a new
warning suppression in this export. `status` reads the current setting; `full`
and `outline` save it for the current user; `selftest` temporarily changes it and
attempts restoration, reporting failure if verification fails.

The six source profiles do not close every installed HAL/network/input binary's
corresponding-source and build provenance. A complete component-by-component
installed inventory and clean-machine build remain release gates. No binary
assets are included while those gates remain open.
