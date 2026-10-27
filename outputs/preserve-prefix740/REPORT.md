# 740: kernel setup prefix preserving CR1b, CR22 and CR33

Fresh diagnostic derived from authored733 sources; no closed runtime reused.
Eleven MMIO and three CRTC setup writes, followed by15 full-value checks.
CR1b is never written and is compared against its actual saved byte85. CR22
and CR33 are not written. All20 cleanup fields retain exact full-value checks.
This is a distinct preservation control, not a704 predicate waiver, bit7 mask,
functional driver patch, full modeset, native handoff or Windows qualification.

Build and56 compiled COFF probe cases,2353 layout cases, linked probe/layout/
main bytes, independent schema mutations and exact source delta review pass.
Models describe counterfactual responses and do not prove hardware behavior.
Full code, manifests and checks are frozen in sources001/review001.

Unique E/Applications/XWNMode740. No startup hook. One authorized launch;
flush/readback reports then automatic dashboard return after15seconds.
Visual observation is not required or inferred. Audit uses persisted raw values.
No geometry/encoder writes. Protected launchers and normal720p untouched.

Staged and exact readback verified; no physical execution result yet. See NEXT.md and latest receipts.

## Physical result: CLOSED

One accepted launch21:39:46UTC, seven reports collected once after authenticated
dashboard return. All15 checks pass, status740, cleanup mask0, selectors restored.
Actual kernel CR0/3/4=8001003b/f000/610; EFLAGS246/46/246.
CR1b before/check/after85/85/85; CR22fe/fe and CR3311/11. Original saved11 MMIO
and4 CRTC values match733. Recovery restores6303 and CR1951.
Full source/binary/stage pins and unrelated E entries verified. Visual color
not observed; automatic firmware return inferred from recorded restart request
and authenticated dashboard. This is not a Windows restart. No hook installed.
No execution/build/stage/collection/audit failure. No owned process/VM remains.

Next: fresh native counterpart of the same preservation control with independent
CPU/relocation/ownership/report validation. It will hold for a photo and requires
watch/reset availability before launch. No new full-mode driver admission.
