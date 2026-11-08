# Moving development to another machine

Recreate the build environment from the repository using
[Environment setup](ENVIRONMENT-SETUP.md). A WSL export or copied SDK installation
is not required. Transfer only the private inputs needed for your next task.
Clean-machine import and bootstrap validation remain pending. Read [current status](current-status.md) and the latest
[continuation](../outputs/engineering-notes/CONTINUATION.md) first: later
observations supersede earlier handoffs. A Git clone alone does not contain the
private inputs, recovery material, local build products or all evidence. The [November 8 migration report](../outputs/migration-20261108/REPORT.md)
and [inventory](../outputs/migration-20261108/INVENTORY.md) describe an earlier,
larger export and host-specific locations; they are historical records, not
an inventory of the lean transfer.

## Choose what to transfer

For routine development, clone the repository and follow the fresh environment
setup. Transfer the ready-to-deploy profile ZIPs and the essential privately
owned media needed for your work separately. Keep private media and packages
outside the public checkout. A WSL export, old SDK, historical disk images,
build outputs and the old private package-input export are not part of this
lean transfer. The ready ZIPs are finished packages; their presence does not
establish that the original intermediate archives, hives and overlays required
by the historical assembler can be regenerated from them or from an ISO.

If the old machine is still available, record its revision and review any local
changes before relying on the clone. Recreate credentials privately and review
console recovery needs separately. The lean transfer does not preserve VM disk
backing chains, console-specific backups or historical private evidence; a
future task requiring one of these needs a separate source for it.

## Package inventory and current evidence

The five private ZIPs below are relative to `D:\xwn844`; their Windows and
profile data must stay private. Verify each SHA-256 against the index after
transfer. These are distinct matched profiles, not interchangeable components.

| Archive | SHA-256 | Evidence and limits |
| --- | --- | --- |
| `xbox16-720p-002/xbox16-720p-002.zip` | `b711fe0f7d660f1eb921bbfef902c174bb45616eb6c522ee6971dee48a3ca81d` | 845: physical 1.6 desktop and mouse observed. Shutdown, repeat boot and persistence untested; earlier 843 shutdown stalled. |
| `xbox10-720p-002/xbox10-720p-002.zip` | `e1837395ac915fd1446bf115fc713a9e267df9c79667a2cff018f11cb8415915` | 846: physical 1.0 desktop and Start observed, return after Restart reported. Resolution readout, mouse, power-off, shutdown-log audit, repeat boot and persistence untested. |
| `xbox10-480p-001/xbox10-480p-001.zip` | `02dac3111407e5f5bae2bab94e534ba4fd83f8cbc8f8f79dbefb5bdf5cbab032` | **Hold:** 852 diagnostic indicated a retrace-status edge timeout, with exact edge and cause unknown. No Windows boot established. The assembled package has not been physically tested. |
| `xbox10-1080i-002/xbox10-1080i-002.zip` | `ef1a678f47a3ad9d429df4264acdac487f025ab390a41b071fc15360b881c738` | Not physically tested as an archive; historical text gaps and motion/field defects remain unresolved. |
| `xbox10-1024x576-f-002/xbox10-1024x576-f-002.zip` | `1e697fadce0e462927b74a5c8e20ce88ba2d6b3dbe0572404cfecba0866deb5f` | Emulator desktop, Start and mouse observed; wizard remained. No physical E boot, normal shutdown or persistence qualification. |

Test 853 was staged; no result was observed. Do not infer a boot or promote
its diagnostic into a package qualification. Consult the latest continuation
and the index's linked known-issues and evidence files before further work.
The historical 587 hardware kit reuses the qualified 421 scanner; its Windows
kit is a private snapshot, not a qualified fresh installation on another console.

The ready-to-deploy set contains these five ZIPs, with the delivery index
and associated issue and evidence records. Verify each ZIP against the hashes
above after copying it. The 480p package remains on hold; the evidence limits
in the table apply even when a checksum matches.

## Rebuild scope

A fresh clone and the public dependencies can reconstruct the eight supported
component profile trees and build them using the documented toolchains. They
do **not** currently provide a verified one-command rebuild of the latest 844
boot chain or its complete Windows packages. The 844 source lineage requires
portable versions of nine historical preparation stages and a checked replay;
see [the source-lineage guide](BUNDLE-SOURCE-RECONSTRUCTION.md). The existing
package recipes pin private intermediate ZIPs, overlays and records. The lean
transfer omits the historical package-input export, and neither the retained
ready ZIPs nor Windows media have been verified as substitutes for those exact
inputs. Reassembly therefore requires additional reconstruction and validation;
do not claim that a fresh clone and ISO alone recreate the delivered ZIPs.

## Set up the new host

Install Git, Python 3.12 or later, Linux or WSL, and the build prerequisites
listed in [building](building.md). Python 3.14 is separately required for the
archive restore helper. Clone the public repository and check out the reviewed
revision; restore reviewed local changes separately:

```sh
git clone https://github.com/PaulMDemers/xbox-windows-native.git
cd xbox-windows-native
git status --short
git rev-parse HEAD
python3 -B tools/xwn.py list
python3 -B tools/xwn.py verify
python3 -B tools/check-repository.py
python3 -B -m unittest discover -s tests -v
```

These are host checks; they do not launch an emulator or console. Review any
failures rather than assuming a new host matches the original. CI runs the last
three checks with Python 3.12 on Linux. Keep at least 20 GiB free on the output
filesystem and the WSL backing volume; fresh build directories belong outside
the repository, source cache and toolchain, preferably on the Linux filesystem.

For component builds follow [building](building.md) exactly. The pinned public
inputs are in [dependencies.json](../upstream/dependencies.json): ReactOS
`afc0127e8f937ab68503d715d948844973756aa1`, Cromwell
`9fc54d0c7cbed7bc3c70373642d833684853011f`, and RosBE Unix 2.2.1 archive
SHA-256 `d720c0a77dc08c6da3929fd282de3fe7af6d697b6fb104889a0362e770742565`.
The fetch command retrieves exact public commits anonymously; bootstrap creates
its own RosBE and receipt. GCC 12 for the launcher must match the hash in
[components.json](../upstream/components.json). Receipts record the local
build, not a publisher signature or proof of identical historical binaries.
The eight profiles are independent. A complete one-command clean reconstruction
of the current combined E demo is not established; see [current build
provenance](BUILD-CURRENT.md).

For the packaged 1.6 720p chain, consult the specific source-tree identities,
patches and binary pins in [bundle-boot844](../outputs/bundle-boot844/README.md), including
its 843 boot-loaded FATX driver. Its historical Linux tree was under
`/home/paul/xbox-windows-native/bundle-boot844-source001`; that path is provenance,
not an instruction to copy the old WSL filesystem. The historical recipe also pins private Windows-side artifacts that are not
included in the lean transfer. Use the recipe and its linked build records to
identify and reconstruct those inputs before attempting package assembly. [The source-lineage guide](BUNDLE-SOURCE-RECONSTRUCTION.md) maps
the committed preparations back to the public profile trees. Historical scripts
need path parameterization; the general component commands cover their own
manifest profiles.

The hardware-report utility uses nxdk revision
`58427c078b4ccb0121f359b6b6c536b3b2914976` and its pinned submodules and
runtime libraries. Follow [its build guide](tester-bundles.md#build-the-hardware-report-xbe);
the recorded 421 build used prebuilt SDK libraries. Record the SDK/submodule
identities and toolchain receipt for any new build. Do not overwrite a shared
SDK to match a historical experiment.

## Configure private paths and access

Choose new local paths for dependencies, RosBE, output directories, private
archives, prepared Windows inputs and emulator fixtures. Supply them via the
command arguments and shell variables in the current guides. Examples and old
`outputs/` scripts contain machine-specific paths and attempt IDs; do not run
them as a portable setup. Keep any local path map and credentials in a private
location outside the repository, with access restricted to the account; use the
new host's credential manager or an interactive prompt where supported. Never
put passwords or tokens in command history, tracked files, manifests or logs.
The public dependency fetch deliberately disables Git credential helpers.
Authenticate source hosting separately using the new machine's own credentials.

After copying private artifacts, compare their hashes to independently retained
receipts or sidecars and check the full backing-chain dependencies before using
them. A checksum proves bytes, not license, console compatibility, or that a
package is safe to deploy. Acquire the shared resource lease before any build,
emulator or hardware activity where one is in use; follow [development](development.md).

Use fresh lease state on the new host. Copied process IDs and old lease files
do not establish current ownership. When using several development machines,
coordinate a single owner for each physical console before staging or launching.
Keep credentials and machine path mappings local to each host.

Clean Windows media conversion still lacks a portable registry converter and a
lossless solution for six FATX-incompatible names. The current kit recipes do
not fix that gap. Ftdisk 49 remains a strict qualification failure; boot,
shutdown and hardware/profile support have scoped evidence only. The 1080i
text/motion defects remain unresolved. Keep backups and review the latest
status before planning any installation or physical test.

## Historical package input export

`tools/migration-inputs.py` describes and verifies the historical private
inputs when those files are available. Its `bind` action requires a complete
export containing `originals`, `recipes`, `blobs`, and `manifest.json`; it
cannot manufacture omitted inputs from a ready package. The lean transfer does
not include this export. The guarded 1024x576 recipe also has a recorded source
record hash mismatch; the delivered F-derived helper has hard-coded paths and
has not been made into a portable rebuild. Retain the delivered ZIP and its
index for that profile.
