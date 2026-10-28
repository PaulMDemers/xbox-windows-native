# Test767: native CR19 upper stride, staged; awaiting watched test

Source-only kernel766 probe and native765 frontend; all older runtimes remain
closed. The kernel counterpart passed10/30/10 with CR13 unchanged80 and all
recovery masks clear. Native execution has not yet been qualified on hardware.

The new payload changes CR19 upper pitch bits after CR17 enable, verifies the
fresh own value and neighbors, then undoes it before inherited recovery. CR13
is read-only. A CR19 recovery or CR13 preservation mismatch inhibits output.
No vertical timing, encoder, PLL, scanout or CR1b/CR22/CR33 writes.

216 result words occupy5100..5460, inside initialized5500. Guard5500..6000
and stack6000..8000 retained. The13 optical rows show signature, final status,
eight aggregate masks and CR19 before/after/own-restored. CR03, secondCR05,
firstCR17 and secondCR02 masks are omitted individually; final success still
requires all twelve masks clear. CR13 values are not displayed individually;
its preservation is represented by the CR19 recovery mask and final status.

Fresh source/payload/host/CPU builds, 253 ELF cases, 243 relocated cases,
76 optical cases, 12 CPU cases, 32 page cases and 372 plan cases passed.
All CPU VMs closed. Source/link review and frozen source checks passed.
Unique E stage and readback passed; console authenticated at UnleashX.
XBE 131072 bytes, SHA256 ed5e0f84ce38b33d9ea49be860db862ba5f2a720253e39b9118bcb3fb4ac8140.

No 767 launch or startup hook. No owned host process/VM remains. Current
watch/photo/reset readiness is needed before the deliberate native hold.
Ordinary launcher and protected720p unchanged. No hardware result for767.
