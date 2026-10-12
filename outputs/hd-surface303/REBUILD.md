# Reconstruction notes for the next clean build

The compiled003 source tree and definitions are in build003.json. The qualified parent is the exact118 index tree4e335dc7a23b4fc058db597a1dded0c098af3cb1, available in the preserved205 source repository. Apply0119-hd-surface-bounds003.patch, not the earlier CRLF patch. Verify the resulting tree and all source hashes against the003 report before compilation.

For a new reusable build command, export the complete Git index with checkout-index into a fresh empty directory, or enumerate every tree blob explicitly. Do not use plain git archive: this parent marks two tracked lwIP metadata files export-ignore, causing an incomplete tree. Initialize/index the complete copy and compare its tree before applying any patch. Use unique output IDs and retain the actual RosBE2.2.1 tool pins. Source reconstruction must not overwrite the existing205 source or consumed303 attempts.

The303 build scripts are immutable records of the executed attempts, including001/002 failures and003 completion; they intentionally refuse reuse.003 compiled from the independently completed parent reconstruction after preserving the exact failed001 source/index tar on D:. Its two cases differ only in XWN_HD_SURFACE_BOUNDS. The inherited XWN_TEXT_BOUNDS remains ON, XWN_BODY_PROFILE and XWN_UC_STORES remain OFF, and shared framebuffer remains ON.

Preserve the20GiB projected C: backing-volume guard, even when artifacts go to D:. Acquire the project build lease. A future fresh command should give the tree-only repository an explicit deterministic build-version identity or document its absent-HEAD diagnostics. These notes describe the corrective procedure; a second fresh end-to-end reconstruction has not been executed or claimed byte-identical.
