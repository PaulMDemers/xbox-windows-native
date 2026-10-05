# Engineering handoff: native Windows on Xbox

Written against the 0.1.0 physical milestone. These notes consolidate the main
lessons; the linked patches, reports and retained private artifacts are the
detailed lab record. Findings from Windows/ReactOS are not automatically bugs
in any Linux FATX implementation. No external project has been contacted.

- [FATX findings and Linux-oriented review checklist](FATX.md)
- [Boot, memory, display, network and validation notes](PLATFORM.md)
- [Video performance and modes plan](../video-next/PLAN.md)
- [Video diagnostic lifecycle and emulator/hardware divergence](VIDEO-DIAGNOSTIC-LIFECYCLE.md)
- [Live framebuffer mapping audit](../video-mapping-audit/README.md)
- [Direct-RAM video prototype and remaining lifecycle work](../video-direct-map/README.md)
- [Detached startup and strict shutdown audit](../video-startup-detached/README.md)
- [Experimental display replacement and failure cleanup](../video-surface-lifecycle/README.md)
- [Preserved baseline and recovery](../release-0.1.0/README.md)

Evidence vocabulary: **physical** means this console; **user-observed** means
the user's report; **emulator** means a named fixture; **compiled test** is a
targeted ABI/behavior test; **hypothesis** is not a root-cause finding. Do not
collapse those into a single PASS. Historical failures remain useful even when
the current candidate passes a later bounded workload.
