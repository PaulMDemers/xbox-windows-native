# Fresh native component reconstruction

`tools/rebuild-native.py` reconstructs a private ReactOS checkout from the pinned
base, verifies the exact candidate0088 ordered patch tree, and builds selected
components in new directories. It never reads Windows media, deploys, changes a
dashboard, or launches a guest. This is the first part of a repeatable release
builder, not yet a complete installer or a replacement for the captured 0.1.0
recovery bundles.

`inputs.json` pins all patch bytes, the manifest, selected installed RosBE tools,
explicit build definitions and expected output paths. It does not lock every
host library, binutils or compiler support file. The existing RosBE 2.2.1
installation was built locally with a Ninja bootstrap compatibility adjustment;
rebuilding that environment from its archive is a remaining portability gate.

## Run

Prerequisites: Linux/WSL, Python 3.11+, Git, the existing pinned RosBE installation
and a local ReactOS Git cache containing the specified upstream revision. Source
and build outputs should live on native Linux storage. The source cache is
read-only input; the new repository fetches its own objects without alternates.

Run under the host's cooperative build lease. Example command inside that lease,
with paths chosen for the local installation:

```sh
XWN_BUILD_LEASE=held python3 /path/to/repo/tools/rebuild-native.py \
  --source-cache /path/to/reactos-cache \
  --rosbe /path/to/RosBE-2.2.1 \
  --output /path/to/new-build-attempt --profile all
```

On the current Windows host the lease wrapper is
`C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build`;
execute the command through WSL in its `-Action` block. This is local integration,
not a required path for another developer.

Profiles:

- `fatx`: candidate0088 vfatfs with the NT5 SLIST compatibility define.
- `boot`: physical-F freeldr, rosload and HAL with diagnostic video flags off.
- `video`: dimensions miniport with trace/PnP/diagnostic flags on, matching the
  working configuration's intent. These flags must not be silently disabled.
- `all`: the three independent configurations above, sharing only source.

The output directory must not exist. Failed attempts retain logs and a failed
report; use a new directory after correcting the cause. Each attempt records the
verified Git tree, actual commands, CMake caches, timestamps and output hashes.
The report says `compiled` only if every selected output exists after successful
build commands. Compilation is not emulator or hardware qualification.

## Remaining complete-build gates

Add the separately patched Cromwell launcher, boot-video and network/input
drivers, host toolchain provisioning, installation config and optional local
media assembly. Compare the exact installed 0.1.0 artifact inventory, including
all dependencies and flags. Build twice in distinct clean directories, assess
timestamp/path differences and validate an assembled owned emulator fixture.
Only then describe this as a repeatable complete bootable-system creation flow.

## Initial reconstruction evidence

Two independent clean source/build attempts completed all profiles:
[001](build-001.json), [002](build-002.json). Both reconstructed source tree
`adf9b3d166ef84630a48d7393fcc9fe3ce78f104` and compiled all five outputs.
The [comparison](repeat-comparison.json) found equal file sizes but 4–13 differing
bytes per artifact. Executable code sections compare equal in the PE outputs;
some data/export sections differ. The differences require analysis before a
deterministic-binary claim. Neither attempt was booted or installed, and neither
replaces the qualified physical 0.1.0 files. Full logs, CMake caches and binaries
remain in the separate native `reconstruction-001` and `reconstruction-002`
directories; compact reports are tracked here.

Attempts 001/002 used [the original input lock](inputs-used-001-002.json), whose
manifest digest covered raw JSON bytes. The final recipe hashes canonical JSON
metadata so LF/CRLF checkouts agree, while keeping patch hashes byte-exact.
[Attempt 003](build-003.json) validates all five outputs with that final recipe.
[Guard checks](guard-checks.json) verify line-ending equivalence, missing-lease
rejection and refusal to overwrite an earlier attempt. No binaries were deployed.
