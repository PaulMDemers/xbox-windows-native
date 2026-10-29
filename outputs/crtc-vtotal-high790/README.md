# CR07 vertical-total overflow control790

Kernel-context diagnostic, not a video driver or full mode switch. Source-only
extension of CLOSED788 after native789. Retained704 crtcvtotal524 gives CR07
(74 & DE) | 20 | 00 = 74. This is a same-value preservation check: dropped writes
and dropped undo are indistinguishable from the successful readback.

654 actual compiled-COFF cases passed, including40 new baseline/readback/coupling/
recovery cases, all614 prior cases and strict reverse ordering.2353 compiled
allocation-layout cases,10 actual clock-fragment cases and linked PE/XBE checks
passed. Independent source/schema review includes shared-register corruption
propagation and output-enable inhibition. No physical result yet.

Build: pinned nxdk58427c0 via build.py under the shared build lease. Run model.py,
layout_model.py and clock_model.py under the xemu lease with XBOX_XEMU_MODE=exclusive.
Run link_review.py, layout_link_review.py, main_link_review.py and review_prepare.py
on a fresh kit/private directory. Existing receipts are immutable, not rerunnable
attempt slots. restore_model.py reconstructs the exact public text-split receipt
without executing a runtime. No binary or credentials are public.

One accepted or uncertain SITE must never be repeated. Private connection.json,
exact stage/readback and bounded automatic return are required. No startup hook,
Windows changes, consoleC or ordinary launcher changes. Fresh native counterpart
requires a new layout proof: its enlarged result would overlap789's IDT.
