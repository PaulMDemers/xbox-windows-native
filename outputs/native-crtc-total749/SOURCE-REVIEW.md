# Native CR00 checkpoint749

Source-only747 frontend/bridge plus physically qualified748 probe. Probe changes
only namespace and native CPU admission: pagingdisabled,CR3zero,IFclear,nonPAE,
establishedcache state. No new control-register or interrupt writes in probe.
124words496bytes end52f0, below reserved5300. Exact18 ELFrelocations,13absolute.
Own32KiBallocation, framebufferbounds, alias/page/overlap checks retained.

Admit ownCR00c8 withCR11bit7clear; target5c is original(779/8)-5. Fullbyte
andCR04/05interaction checks. Restore ownCR00 thenCR05/04 thenH7/prefix.
CR00,CRTC orH7recoveryfailure preventsoutputenable. Novertical,pitch,scanout,
encoder,clock,CR1b/22/33writes,fullmode orWindows. Modelproof is control-flow
andaccess contract only; nativehardware behavior remains a fresh question.

13opticalrows: signature,return,forward,prefix/H7/CRTC/CR00cleanupmasks,
CR00before/after/restored,selectors,nativeCR0,CR05afterCR00. CR00target5c is
frozen build contract. CR04after/CR04and05restoration,CR3/4,individualH7 are
unexposed; aggregatepredicates only. No postnative diskpersistence. Deliberate
hold needs currentwatch/photo/resetreadiness after fullstaging verification.
