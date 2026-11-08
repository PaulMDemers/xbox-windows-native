# Machine migration preparation

Prepared November 8, 2026. Start with [the migration guide](../../docs/MIGRATION.md).
Private transfer material is under `D:/Xbox-Windows-Migration/2026-11-08`.
The original storage remains available for destination validation and historical
disk-chain recovery. No console or emulator was launched.

## Source and portability

Pending diagnostic source for 849 through 853 was reviewed and committed with
exact bytes preserved. Private raw histories, captures and local deployment
inventories remain excluded from public Git. README and current handoffs now
reflect the packaged 1.0/1.6 results and the outstanding 480p investigation.

An independent shallow checkout exposed line-ending changes in pinned receipts
and eight matching authored sources. Commit `08b55c3a` preserves those bytes
with scoped Git attributes and regression tests. The fresh checkout then passed
all eight source-profile checks and all four migration tests. See
[fresh-checkout.json](fresh-checkout.json).

The existing host suite completed 137 tests with 10 platform skips before the
migration tests were added. The final public payload scan passed across 54,417
tracked files; the two new closing report files were reviewed separately.
Changes add the reviewed migration helper, tests, documentation and exact-byte
preservation. There was no driver behavior
change in this maintenance work.

## Private transfer material

- `Ubuntu-build-environment.tar` is a completed stopped WSL2 export containing
  133,735,434,240 bytes. All 6,569,644 entries were parsed and two pinned boot
  source samples matched. Archive SHA-256:
  `3e12f1d6f5d775d89b1d64eb66d24379bb8870726858088617d6fd8542ece28f`.
- `windows-toolchains.tar` contains nxdk, MSYS2 and Homebrew wrappers. All
  60,402 archive entries were read, regular-file hashes recorded and five key
  tools matched against the source. It is 3,991,723,008 bytes with SHA-256
  `6f100827f6205440894c19580c295e8e03e56307b5f4b3b8d57caa69ddf1bb33`.
- Archived Clang 22.1.8, lld-link and llvm-ar binaries match the actual
  MSYS2 build-wrapper paths. nxdk is pinned to
  `58427c078b4ccb0121f359b6b6c536b3b2914976`.
- `package-inputs` contains 22 pinned files totaling 662,967,386 bytes, original
  recipes and derived path mappings. Both the export and independent review
  verified the blobs. Four recipes' public receipt pins match the fresh checkout.
- `release-packages` contains all five release ZIPs and their referenced issues,
  indexes and evidence: 18 files totaling 1,630,975,664 bytes, copied and
  hash-verified against `DELIVERY-016.json` and source metadata. The original
  packages remain under `D:/xwn844`.
- Private root, workspace and toolchain inventories describe the additional
  archives, recovery data, ignored workspace files and attachments. The old
  October 26 archive and raw disk chains remain available separately.

The guarded 1024x576 recipe retains an unresolved historical `build004.json`
receipt mismatch and is marked unavailable. The separately delivered F-derived
package has its own lineage and requires manual path remapping for reconstruction.
The delivered ZIP remains available with its emulator-only qualification.

## Cleanup and limits

Removed 6,573 duplicate files from the 1.6 720p staging tree after independent
SHA-256 comparisons and a final complete metadata/path check. Logical content
removed was 704,331,253 bytes. Its verified ZIP and records remain intact.
The private cleanup plan, per-file journal and completion receipt record the
operation. See [the inventory](INVENTORY.md) for the broader retention findings.

Automatic command approval rejected recursive removal of the clean temporary
validation checkout with the reason "blocked by policy." The command did not
execute. `C:/xwn-migration-check-20261108` remains present; it contains no required
private build inputs. No alternate deletion method was attempted.

New-computer WSL import, toolchain extraction, complete builds and hardware
tests remain pending. Host archive and source checks do not establish those
outcomes. Before further console work, establish its actual current state and
resolve Test853's missing observation. Copied lease files and process IDs do
not establish ownership on a new host.
