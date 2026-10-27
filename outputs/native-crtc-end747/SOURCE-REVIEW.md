# Native CR05 checkpoint747

Source-only745 frontend and bridge plus physically qualified746 probe. Probe
changes only namespace and native CPU guard: paging disabled, CR3zero, cache
disabled as established, IFclear, non-PAE. No new CPU or interrupt state change
inside the probe.116words464bytes end52d0, below reserved5300. Exact18 ELF
relocations,13absolute; own32KiB allocation and independently checked pages.

Preserving prefix/H7/CR04 precede CR05 low-five write. Preserve own upper bits,
full-byte target3e and CR04=5d required. Reverse CR05/CR04 own-value recovery
before H7 and prefix recovery. No output enable after H7/CRTC recovery failure.
No new functional Windows or complete mode replay. No kernel video recipe
borrowed into native code. Host models are access/control-flow proof only.

Thirteen optical rows: signature,return,forward,prefix/H7/CRTC cleanup masks,
CR05before,target,after,restored,CR04after,selectors,nativeCR0. Exact416bits
will require photo evidence. CR3/CR4 and individual H7 words are not exposed
optically. Pre-arm kernel files do not contain native results. Intentional
hold requires user watch/photo/reset readiness after staged preparation.
