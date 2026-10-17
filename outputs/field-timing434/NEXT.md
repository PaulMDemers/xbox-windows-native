# Next discriminating software comparison

Keep the 720p Windows default. The current probe is closed; do not rerun it or
change timing/filter/pitch registers experimentally without a defined contract.

Review the complete normal nxdk/PBKit scanout initialization and restoration path,
especially the PCRTC_CONFIG address-mode difference (stock API leaves 3; PBKit
sets 2). Determine its exact latch/address semantics and dependencies before
using it. A source comment or generic NV04 bit name alone does not establish
NV2A field-fetch semantics. No evidence yet justifies a Windows driver patch or
a manual IRQ row-offset toggle. Likewise the SD encoder FLD_MODE control is not
an HDTV fix according to the manufacturer's documentation.

A useful next control is an owned standalone graphics-initialized path with the
same independent row pattern, contrasted against the closed mode-API-only path.
It must use its own allocations/channels and normal supported initialization,
record all scanout changes, verify actual framebuffer/stride/pixels, and identify
any additional variables. If that comparison changes the visible result, narrow
the cause with evidence before porting a change. A raw register cadence match
cannot qualify pixels on the display. User observation or an independently
validated output capture is needed for that part. Do not silently substitute an
emulated field counter, invoke a proprietary host binder, borrow firmware GPU
objects, or promote a broad initialization difference as a one-register fix.

If no supported renderer-init difference accounts for it, the remaining boundary
is actual odd/even memory fetch and the GPU-to-encoder/HDMI field interpretation.
Changing only the adapter remains a useful isolation experiment, not a required
purchase and not evidence that the current adapter is faulty. The row-selection
model, 720p result and identical behavior on two displays all remain valid.

Other public-release work remains the 429 FATX image-discovery/native integration,
clean-install validation and tester bundles. No release tag or 1080i promotion.
