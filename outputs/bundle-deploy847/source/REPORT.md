# 847 profile-controller review report

Prepared host-side source and offline fixtures for fixed Xbox 1.0 profile
transitions. No console FTP was performed by this task; the 846 operator owns
the only physical session.

## Package evidence

- Verified the 480p archive (`02dac3111407e5f5bae2bab94e534ba4fd83f8cbc8f8f79dbefb5bdf5cbab032`, 326,269,059 bytes) and 1080i archive (`ef1a678f47a3ad9d429df4264acdac487f025ab390a41b071fc15360b881c738`, 326,268,424 bytes) against their complete ZIP manifests.
- Independently compared all 6,568 E files in the 720p, 480p and 1080i package manifests. Exactly two paths differ: `default.xbe` and `xwnfatx.sys`. The other 6,566 files share canonical SHA-256 `5ff67b5019578504472b9ced1da1bb1a1e7e674d911a2dd814b80c8f9e7a99cf`.
- 720p to 480p changes only the fixed-mode XBE. A transition to or from 1080i also changes the FATX driver. Each profile's XBE is written last. The shared startup script is verified and never written. User hives, logs, documents and all other managed-root extras are preserved in place; the current full managed tree is backed up before any transfer.
- 1080i remains experimental: the historic text and movement/drag artifacts are unresolved. Neither assembled 480p nor 1080i archive has been physically boot-tested.

Any later physical observation through this controller would be a test of the
verified 1.0 mode-specific file delta on top of a previously booted common tree
with mutable user hives, logs and documents. It would not establish a
first-install boot from the exact full ZIP. The common-tree digest is an
archive-to-archive comparison; it is not asserted for the live E tree after
Windows changes it. Preflight, transfer and launch recheck the immutable boot
chain, including `freeldr.ini`, HAL, Xbox boot video, `ntoskrnl.exe`,
`bootvid.dll`, the Xbox video miniport and Windows video support files.

## Guards and limits

- Target revision, source profile, endpoint and two preserved historical owner markers are checked; the F-volume owner marker is also checked against the pinned evidence. The 846 receipt and local marker preimages must verify.
- Every attempt has a profile-specific lock and receipt. The shared 846 helper adds the cross-profile host lease and hardware-ticket check. Incomplete/uncertain transfer journals are not retried. Launch is a separate one-shot operation with durable intent and no automatic retry.
- The controller requires a recent conservative E capacity receipt before transfer and retains a 20 GiB host reserve. No operation changes dashboard C, saves, firmware, keys, startup or live Windows display settings.
- Preflight failure 846/001 is preserved in `PREFLIGHT-001-FAILURE.json`: the old listing parser incorrectly applied its per-file capture ceiling to an unrelated 805,306,368-byte root item. The corrected scanner lists root entries but downloads only selected managed roots and explicitly pinned markers; selected files are streamed. The mock fixture covers that root item.
- A separate 846 root-key casing defect was fixed for future receipts: `/E` is now keyed as `/e` internally and remains present in the package directory map. Its regression checks the root mount path explicitly. The frozen 846/002 receipt is not rewritten by this change.

## Offline checks

- `python outputs/bundle-deploy846/source/test_preflight.py`: 6 passed.
- `python outputs/bundle-deploy847/source/test_profiles.py`: 7 passed.
- No FTP connection, upload, launch or console-side mutation occurred during these checks.

The 847 scripts are prepared for parent review. Their future physical use remains
separate from their offline test results and requires the 846 operator workflow.
