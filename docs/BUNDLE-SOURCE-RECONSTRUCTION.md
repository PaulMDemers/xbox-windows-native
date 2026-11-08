# Reconstructing bundle-boot844 sources

This guide describes source reconstruction only. It does not build binaries,
assemble private Windows media, or launch an emulator or console. It uses the
tracked source records and patches; a 130 GB WSL backup is not a prerequisite.

## Pinned starting trees

The 835 source preparation starts from the exact public-base trees already
represented by two supported `xwn.py` profiles:

| Component | Public source pin | Reviewed parent tree | Profile |
| --- | --- | --- | --- |
| ReactOS loader | ReactOS `afc0127e8f937ab68503d715d948844973756aa1` | `b2bb44a126630712c01af6bc331d5d7d9e4f07b0` | `loader` |
| Cromwell | Cromwell `9fc54d0c7cbed7bc3c70373642d833684853011f` | `70c0a6c5aff82537f489e7d18410d5980fa797a7` | `launcher` |

The rows and overlays are recorded in [components.json](../upstream/components.json).
Use the public fetch and `xwn.py source` procedure in [building.md](building.md)
to materialize those two trees in fresh Linux or WSL output directories. The
profile trees are the parents used by [prepare835.py](../outputs/boot720-review833/prepare835.py).

The 843 FATX tree is a separate branch. Its exact base is the same ReactOS
commit, with the ordered patch series in
[fatx-directory-order/manifest.json](../outputs/fatx-directory-order/manifest.json).
The series has 87 pinned patches; all listed patch files are present in this
repository. From a clean checkout of that exact ReactOS commit, run:

```sh
python3 tools/apply-series.py --source "$FATX_BASE" --manifest outputs/fatx-directory-order/manifest.json
```

`FATX_BASE` must be a fresh checkout of the pinned ReactOS commit, outside the
repo; the command verifies the complete patch series and result tree
`8e12297ca0ed53383fe9aaebef152c26aee5a43b`. The supported `fatx` profile has
a different tree and is not a substitute for this branch.

## Source-only lineage

The historical source lineage follows this order; it is an adaptation map,
not an executable replay script. Each script records its expected parent
and writes a `source00*.json` tree record. Keep those checks: they detect a
wrong parent, incomplete patch series, or changed source.

| Order | Tracked preparation | Source input and purpose |
| --- | --- | --- |
| 1 | [prepare835.py](../outputs/boot720-review833/prepare835.py), then [fix-source002.py](../outputs/boot720-native835/fix-source002.py) | Public-profile launcher and loader trees; creates 835 and its `source002` correction. |
| 2 | [prepare-source.py](../outputs/boot720-root836/prepare-source.py) | 835 `source002`; applies the 836 root-chain change. |
| 3 | [prepare-source.py](../outputs/boot720-cache837/prepare-source.py), then [fix-source002.py](../outputs/boot720-cache837/fix-source002.py) | 836 launcher/loader plus the FATX directory-order tree; creates 837 and its `source002` correction. |
| 4 | [prepare-source002.py](../outputs/boot720-fatpage838/prepare-source002.py) | 837 `source002`; this is the variant used for the recorded `boot720838-source002` directory, whose receipt is `source001.json`. It creates a fresh 838 tree and applies the FATX metadata-page change. [prepare-source.py](../outputs/boot720-fatpage838/prepare-source.py) is an alternate full preparation from the same parent; do not run both. |
| 5 | [prepare-source.py](../outputs/boot720-rootchain839/prepare-source.py) | 838 `source001.json` from directory `boot720838-source002`; applies the 839 FATX root-chain change. |
| 6 | [prepare-source002.py](../outputs/boot720-load841/prepare-source002.py), then [source-review002.py](../outputs/boot720-load841/source-review002.py) | 839 `source001`; the full preparation creates directory `boot720841-source002` and writes `source001.json`. The incremental observer review updates that directory and produces `source002.json` consumed by 842. The earlier `prepare-source.py` is an alternate full preparation from 839; do not apply both. |
| 7 | [prepare-source.py](../outputs/boot720-bridge842/prepare-source.py) | 841 `source002`; restores the existing AGP bridge setup while retaining GPU state. |
| 8 | [prepare-source.py](../outputs/boot720-input843/prepare-source.py) | 842 `source001`; namespace-only 843 reproduction. It also copies the tracked utility sources and build/host scripts from the 842 input folder. |
| 9 | [prepare.py](../outputs/bundle-boot844/prepare.py) | 843 `source001`; changes the two XWN16Boot843 names to XWNEBoot and records the resulting tree. [setup.py](../outputs/bundle-boot844/setup.py) copies the tracked utility sources from `boot720-input843`. |

The number 840 refers to a separate PCI inventory utility and is not a source
tree step. Source records are not uniformly named after their source tree:
follow the parent tree IDs and the consumed `source00*.json` named above, not
the directory number alone. The preparations above are source transformations
only; use each folder's patches and records as evidence, not the historical
build or hardware records as instructions to run.

## Adapting the preparations

The historical preparation scripts are not portable as-is. They hardcode
`/home/paul/xbox-windows-native` and `/mnt/c` paths, require the historical
`XWN_BUILD_LEASE=held` environment variable, assert specific output paths do
not exist, and some write records or patches into their source folders. Do not
run them verbatim or overwrite their evidence.

Some tracked utility sources already contain their final amendments; replaying
a prior preparation against those files can differ from its original receipt.
Use the recorded before/after hashes and patches to distinguish historical
intermediate bytes from final sources. The entire chain has not been replayed
in this documentation pass.

For a portable reconstruction, create a separate workspace outside the repo
and parameterize each script's repository root, prior source input, and new
output root. Copy the source-generation logic and use unique, fresh output
directories. The historical `XWN_BUILD_LEASE=held` check is only a marker;
follow the current host's shared-work coordination before writing, and do not
pretend setting the old variable acquires a lease. Retain all parent-tree,
source-hash, patch-hash, and result-tree checks. Write new run records outside
the tracked historical folders. Keep source exports independent of build
directories and do not invoke build, staging, qualification, physical, or
emulator scripts.

At each transition, compare the resulting `git write-tree` value with that
step's tracked `source00*.json`. At the end, verify `outputs/bundle-boot844/source001.json`:

- Cromwell parent tree: `6d786c41b664235c4a2c270eddaa8ecd45ec98e6`;
- ReactOS parent tree: `09013225f75260cd6ff34441c886c1c92c536aa1`;
- resulting Cromwell tree: `9ba716fdbb587d021cbfc73f666a9fe96b4810ec`;
- resulting ReactOS tree: `54b4047042b614f6d2e3e50ce22b66d42430eefe`.

The 844 record describes a source-only result. It does not recreate the
historical compiler installation, generated binaries, private Windows package,
or physical qualification. The broader migration guide remains useful for
those separate inputs: [MIGRATION.md](MIGRATION.md).
