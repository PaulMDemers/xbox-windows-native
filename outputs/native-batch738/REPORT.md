# 738 staged: native deferred safe-prefix check

737 established first/reselectedCR1b85 after CPU work in a minimal native
sequence, with cleanup successful.738 asks a different question: does the
native safe prefix reject under733's original deferred check order, without
any inserted delay or CR1b sample block?

Probe body is identical to733 except namespace and explicit native CPU admission:
CR0 masked e0000001 equals40000001, CR3zero, entry/criticalIFclear, PAEclear.
Eleven MMIO writes, four CRTC writes, then fifteen ordered full-value checks.
Recovery compares all20 saved fields and restores selectors. Stops beforeCR22/
CR33 writes, geometry, encoder programming or full mode replay. The original704
writes additional registers before its check, so738 cannot alone attribute
708/709's failure or qualify a functional driver change.

Validated737 native handoff/page/frontend reused as authored source, with the
fresh ELF's exact ten absolute relocations (fifteen total) replacing its former
one. Result has76 raw words. Optical13-row report exposes phase, returned status,
forward status, first mismatch, full32-bit expected/observed, cleanup mask,
selector status, actual nativeCR0/3/4 and checks completed. No mask or truncation.
Native final results require a photo; disk reports are kernel preparation only.

No physical launch yet. All validation passed:56 actual ELF cases,12 fresh
CPU fixtures (all closed),53 relocated integration cases,76 full-framebuffer
optical cases,20 nxdk page-builder cases,372 nxdk ownership cases and131379
host ownership cases. Exact linked object/bridge/payload and frozen sources
verified. Fresh stage and byte-for-byte readback passed at
E/Applications/XWNMode738. No new build/test/stage failure. Final Git whitespace review flagged two
whitespace-only lines in the executed integration harness. The failure is kept
in whitespace-review001; frozen bytes are retained deliberately, and every
other staged path passed whitespace checking. Hardware predicates are unchanged.

XBE SHA256: 085e8ebf9f50bc04efc8af11e3838cb5769a7b8102a112c99d42f78eec3cfd89.
All737/prior runtimes closed; no closed runtime reused. Protected720p and
ordinary launchers unchanged. No hook. Networking/boot/1080i remain separate.
