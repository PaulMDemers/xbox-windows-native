# Test745: native CR04 counterpart, preparation only

Closed kernel744 physically passed CR04 a7->5d->a7 with CR05 unchanged31
and all prefix/H7/CRTC recovery checks passing. This distinct probe takes that
exact transaction into native context with the previously qualified743
frontend and bridge. The probe differs from744 only by namespace and explicit
native CR0/CR3/CR4/IF admission. No closed runtime is reused.

The112-word result occupies5100..52c0 within the reserved5300 boundary.
The13-row report exposes signature, return/forward status, three cleanup masks,
CR04 before/checked/restored, selectors and actual native CR0/CR3/CR4. The
individual native CR05 and H7 values remain unexposed; summary predicates alone
cover those checks. Kernel744 raw values cannot substitute for native evidence.

There is one additional CRTC data write, CR04=5d, after the preserving/H7
prefix. Undo CR04 using this run's saved byte, then reverse H7; neither recovery
may fail before output-enable. CR05 is never written. A failed restore may
leave the screen black. Native code deliberately holds and cannot persist its
post-handoff result to disk. Preparation reports are separate kernel evidence.
Current watcher/photo/reset readiness is required before a single launch.

No CR05/other new CRTC geometry, vertical timing, encoder, scanout, clock,
full-mode or Windows work is admitted by this preparation. Ordinary launcher,
protected720p and prior releases remain unchanged. No startup hook is used.

Preparation completed:98 ELF cases,12 fresh disklessCPU contexts/refusals,
88 relocated integration cases,76 optical cases,32 nxdk page-builder cases,
372 nxdk ownership cases and131379 host ownership cases pass. All VMs closed.
Source/linked review passed. Padded payload9916bytes (4472unpadded),13 absolute
relocations/18total, result448bytes. Exact XBE SHA256:
6c89d7e48cbaaa0b5f9ff61a1bc6405374d8247dcae89e7faf276996e8e0cd44.
UniqueE stage/readback complete; no745 launch or hook. Current watcher needed.
