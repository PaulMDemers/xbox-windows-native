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
- `support`: NT5 boot-video and NVNET components.
- `all`: the four independent configurations above, sharing only source.

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

The launcher, boot-video and NVNET portion is now implemented below. Remaining
input drivers, config/media assembly and runtime validation are still open.

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

## Eight-component overlay

For a single command that performs all three steps under the host build lease:

```sh
XWN_BUILD_LEASE=held python3 tools/rebuild-package.py \
  --reactos-cache /path/to/reactos-cache \
  --cromwell-cache /path/to/cromwell-cache \
  --rosbe /path/to/RosBE-2.2.1 \
  --output /path/to/new-package-build
```

The output contains independent `native`, `launcher` and `package` directories.
Failures stop the chain and retain the earlier logs; no stale package is reused.
The native build checks a 20 GiB free-space reserve on both its output filesystem
and the actual Windows volume backing WSL. The standalone launcher checks 2 GiB.
These are preflight reserves, not protection against unrelated concurrent writes.
The WSL check resolves the current distribution from the Windows registry and
fails closed if its host volume cannot be identified. See [guard regression](space-guard-checks.json).

`tools/rebuild-launcher.py --source-cache /path/to/cromwell-cache
--output /path/to/new-launcher-build` reconstructs the physical-F Cromwell
launcher under the same build lease. It applies two hash-checked patches in a
new checkout and records GCC identity, patched tree and XBE hash. It currently
requires the installed GCC 12 and host make/link tools; provisioning/pinning the
whole host environment remains unfinished. See [launcher result](launcher-001.json).

The package command is independent of compilation and does not need a build lease:

```sh
python3 tools/package-native.py \
  --native-build /path/to/completed-native-build \
  --launcher-build /path/to/completed-launcher-build \
  --output /path/to/new-package-directory
```

It verifies artifact hashes, requires all seven native outputs plus the launcher,
and emits a ZIP with explicit dashboard E/F destinations and a manifest. Every
archive entry is read back. Windows, registry hives, user files, dashboard,
firmware and startup/config scripts are excluded. This is an overlay for an
already configured owned installation, not a fresh Windows installer or a
hardware-qualified update. Do not deploy it from compilation evidence alone.

Two packaging runs over the same inputs are byte-identical, SHA-256
`2981f6f1c68c8220d2b6bdff728714c0887b99b3d4af2e239768c5d54dd02de7`.
See [package check](package-check.json), [manifest](overlay-manifest.json) and
[negative guards](package-guards.json). Deterministic packaging does not make the
underlying compiler outputs deterministic.

The complete one-command path passed in [pipeline 002](pipeline-002.json):
fresh patch replay, seven native builds, separate Cromwell build and eight-file
package readback. [Package result](pipeline-002-package.json) records SHA-256
`5ada6fb5887227f4c4b50d2197bb7a498342b4cd2f4eab90d81716990d5d30e3`.
The private archive copy is under
`E:/Codex-archive/xbox-windows-native/reconstructed-overlay-20261005`.
This new compilation differs from the earlier package; only repeated packaging
of identical inputs is byte-identical. No reconstructed package has been booted.

Pipeline 001 failed during patch replay when host C: filled. WSL mounted
read-only and could not save its failure report. Closed owned traces were copied
to E:, hash-verified and removed from C:, with per-run relocation pointers.
WSL subsequently mounted writable without a filesystem repair or global reset.
The failed checkout is retained; the successful retry used a new directory.
See [host incident](host-space-incident.json) and [trace relocation inventory](trace-relocations.json).

### HAL configuration correction

Comparing captured 0.1.0 files with fresh outputs exposed a missing opt-in:
`XBOX_NT5_FRAMEBUFFER_ONLY_PCI=ON` is required for the accepted physical HAL's
compatibility view. The old live CMake cache was OFF, so cache inspection alone
would have selected the wrong HAL. Builds 001–004 are retained as compilation
evidence, not baseline-equivalent packages. [Build005](build-005.json) explicitly
enables this option; packaging rejects OFF builds. The compatibility view belongs
to the guest HAL and is separate from the synthetic xemu BAR experiment.
Its BAR2 suppression must be reconsidered before an accelerated GPU driver uses
that resource. No physical files changed during this correction.

[Baseline section comparison](baseline-section-comparison.json) finds exact
`.text` matches for the rebuilt FATX, video, network and boot-video drivers.
The HAL and second-stage loader have code-section differences requiring further
inspection. Equal file sizes and matching source manifests do not prove these
outputs behave identically to the installed versions. Runtime qualification of
the whole overlay remains required before deployment.
