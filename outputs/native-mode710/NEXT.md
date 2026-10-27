#710 CLOSED: cyan held pre-transaction checkpoint observed

Read observation001, collection001, audit001 and closure001. One launch, user
confirmed cyan holding, then manual power-cycle and nine reports collected once.
PCI/CRTC/SEQ/geometry/allocation mappings equal709. All pins and alias audit pass.
No startup hook, host child or Windows. Console at dashboard; no reset needed.
Never relaunch/recollect710,708 or709. Use retained inputs only for a NEW attempt.

Next NEW711: isolate the real transaction call and baseline read/check phase,
with a deliberate observable return/HOLD BEFORE blank(g). Use a distinct
checkpoint result, not T704_OK or an implied successful mode change. Preserve
argument, layout, IF and hardware-baseline rejection; restore indexed selectors.
No encoder, ACPI control or mode-register writes. Native indexed register reads
necessarily select indices; save/restore those explicitly. Test exact relocated
bytes, rejection cases, stack/call behavior, no forbidden I/O/MMIO and bounded
optical output on fresh host fixtures before physical staging. Review changed
payload layout/relocations rather than assuming9916-byte compatibility.

Source boundary: outputs/xcal-transaction704/transaction003.c, after baseline
predicate and immediately before phase2/blank(g). This is the next hypothesis,
not an established fault.710 reached the larger handoff/PCI/timer boundary on
one run; it does not prove every708/709 failure occurred later. Do not repeat the
full native-mode failure until lucky or patch functional video speculatively.

Original720p/ordinary launcher protected, console C off limits. Hardware ticket
retained; build/xemu released; automation paused. Other work remains tabled.
