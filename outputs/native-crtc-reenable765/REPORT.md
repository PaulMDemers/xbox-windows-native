# Test765: native CR17 forward enable and recovery

Source-only extension of closed764 kernel probe and closed763 native frontend.
No closed runtime is reused. The next original source operation enables CR17
bit7 after CR01 and laterCR02. It captures fresh63, writes/readse3, checks all
six horizontal neighbors, then restores63 before undoing earlier writes. Outer
blanking stays applied until recovery admits output enable. No later pitch,
vertical, encoder or PLL work; CR1b/22/33 remain unwritten.

The200-word result occupies5100..5420. The page builder initializes5000..5500;
5500..6000 remains guard space and6000..8000 remains the stack. Fresh page,
CPU, integration and optical tests must pass before physical admission.

The13-row report contains signature, final status, eight aggregate recovery
masks, and secondCR17 before/after/intermediate-restored values. CR03,secondCR05
and firstCR17 masks are omitted from the photo; final765 requires all eleven
masks clear. Same-valueCR02 dropped-write limits persist. Successful restoration
is not proof of a complete native mode switch or Windows1.6 support.

Preparation only. No physical launch, startup hook or Windows launch. Deliberate
native hold requires a current watcher, photo and manual power-cycle afterward.

## Validation and retained reviewer failure

Fresh228ELF,218 relocated integration,76 optical,12CPU(allclosed),32page and
372ownership cases PASS. Independent source/result/guard/report review PASS.
Linked-review003 failed to write its receipt because its copied directory name
was wrong; linked-review-failure001 preserves this. New linked-review004 changes
only that path and PASS. Guest sources and binaries unchanged. Exact tested
sources frozen and Git index bytes verified.

XBE131072bytes SHA256
c49709b60b8207850bdd2a46b5ef729d90b6f4f8d90e4e5614dd48deff581a9a.

Unique E stage and exact readback PASS. Awaiting watcher readiness; not launched.

## Launch

User confirmed current watch/photo/reset readiness. Exact frozen index, source,
build and remote staged bytes reverified. One SITE accepted2026-10-28T04:26:19.182299UTC.
Actual screen/photo pending; no retry, startup hook or owned host process/VM.
