# Moving development to another machine

Use this guide to transfer the source, pinned tools and private package inputs.
Clean-machine import and bootstrap validation remain pending. Read [current status](current-status.md) and the latest
[continuation](../outputs/engineering-notes/CONTINUATION.md) first: later
observations supersede earlier handoffs. A Git clone alone does not contain the
private inputs, recovery material, local build products or all evidence. See the
[November 8 migration report](../outputs/migration-20261108/REPORT.md) and
[inventory](../outputs/migration-20261108/INVENTORY.md) for verified transfer
contents, host-specific locations and remaining validation.

## Preserve the old machine first

1. Record the checkout commit, branch, `git status --short`, remotes and any
   uncommitted or untracked work. Review untracked files before transferring or
   committing them: some are private captures even when their extensions are
   normally allowed. Preserve changes separately until reviewed. Do not clean
   the checkout or retire the old disks until the destination has been checked.
2. Inventory private Windows media and licensing, prepared E trees, console
   recovery/preimage backups, EEPROM/firmware, user data, build outputs and
   receipts, and private package ZIPs and their checksums. Transfer only data
   you are entitled to use, using encrypted private storage. Keep these outside
   the public checkout; never add credentials, Windows files, hives, firmware,
   disk images or private captures to Git or a public release.
3. Preserve VM disk **backing chains together**, their configs and associated
   source/executable identities. Stop writers before copying and verify hashes at
   both ends. Old closed runtimes are evidence, not seeds to launch or parent.
   [Archive restoration](ARTIFACT-ARCHIVE.md) explains the private D: archive,
   its pointer and receipt files, and the Python 3.14 restore helper. Transfer
   the archive and its indexes together if needed; recorded D: paths will need
   mapping on the new host. Preserve the original copies during verification.
4. Preserve the historical private kits in `E:\Xbox-Test-Kits\2026-10-19`,
   and the later profile packages and supporting files under `D:\xwn844`.
   The latest package index is `D:\xwn844\DELIVERY-016.json`. Preserve
   matching preimages, manifests and sidecars alongside them. See the table below.
5. Record the selected xemu source, executable, configuration and disk chain
   when emulator work is needed. [Local xemu changes](xemu-changes.md) describes
   the audited 322 candidate and distinguishes it from stock xemu. Firmware
   and disk fixtures are private; copying a source checkout does not recreate
   them or establish the identity of a different executable.

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

The November 8 migration folder includes a compact `release-packages` copy
of these five ZIPs, their referenced issues/evidence and delivery index. Its
`copied-files.json` records verified hashes. Copy the complete migration folder;
the older `D:/xwn844` staging trees are not required to use these packages.

## Transfer the WSL development environment

The quickest route to the existing development environment is to transfer a
verified WSL export **and** the separately inventoried Windows-host inputs,
private archive, package files and recovery data. The archive alone does not
contain the live WSL toolchains, source/build inputs or all external fixtures.
The current distribution is `Ubuntu` under WSL 2; it was stopped when checked.
An export preserves Linux files, including installed toolchains and potentially
credentials or private data, so protect it as a private backup. It does not
include Windows files accessed through `/mnt/c`, `/mnt/d` or `/mnt/e`.

After confirming there are no active WSL tasks, leases or writers, choose an
unused destination with sufficient free space and export from PowerShell:

```powershell
wsl --list --verbose
wsl --export Ubuntu 'D:\private-transfer\Ubuntu-xwn.tar'
Get-FileHash -Algorithm SHA256 'D:\private-transfer\Ubuntu-xwn.tar'
```

Create the destination directory first; retain the old distribution and record
and independently compare the export hash after transfer. On the new machine,
install WSL 2, choose a new distribution name and an empty private install
location, then import the verified export:

```powershell
wsl --import Ubuntu-XWN 'C:\WSL\Ubuntu-XWN' 'D:\private-transfer\Ubuntu-xwn.tar' --version 2
wsl --distribution Ubuntu-XWN --exec /bin/bash -lc 'pwd; python3 --version; git --version'
```

Import may default to root. Configure the intended Linux user according to the
new distribution's WSL configuration, without exposing credentials. The Linux
home paths in the export normally remain the same; Windows volume letters and
`/mnt/<letter>` paths can change. Restore external inputs to the recorded
locations or update local path variables and configuration deliberately, then
verify each referenced file and disk backing chain. Do not edit historical
receipts to conceal path changes. Re-establish source-host and console access
credentials separately through the new host's private credential store or
interactive prompts; do not rely on copied secrets or publish the export.
Check the imported toolchain receipt and run the host checks below before any
new build. Export/import has not been validated on a new machine.

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

For the packaged 1.6 720p chain, retain the specific source trees, patches and
binary pins in [bundle-boot844](../outputs/bundle-boot844/README.md), including
its 843 boot-loaded FATX driver. Its recorded Linux tree is under
`/home/paul/xbox-windows-native/bundle-boot844-source001`; check its identity after
import. Its pinned Windows-side artifacts are in the private package input
export. Use the recipe and its linked build records when reconstructing
that package. The general component commands cover their own manifest profiles.

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

## Private package input export

After reviewing `tools/migration-inputs.py`, use its `export` action with a new
private destination outside the checkout and input directories. It verifies
pinned input hashes, deduplicates by SHA-256, retains a 20 GiB reserve and
checks every copied blob. It preserves original recipes and produces local
path-remapped copies. On the new host, verify the transferred bundle, then rebind it:

```powershell
python tools/migration-inputs.py bind <BUNDLE> --checkout <CHECKOUT>
```
The manifest contains old private paths and must remain private.

The guarded 1024x576 JSON recipe references build004.json by hash `adaaf528...`,
but the tracked file hashes `290ff7f6...`; the exporter records the discrepancy
and marks that recipe unavailable. The actual delivered 1024x576-F-002 uses the
separate F-derived helper. Its pinned private archives and overlays are included,
but the original helper has hard-coded paths and requires manual path review; no
portable F-derived rebuild is claimed. Keep the delivered ZIP and its index.
