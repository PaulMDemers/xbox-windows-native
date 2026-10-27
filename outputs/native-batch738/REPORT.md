# Test738 closed: native deferred-prefix CR1b rejection

The user observed orange and a held picture. All416 optical bits were decoded
independently from the private photo, with offset/threshold and adjacent-row
cross-checks. Native return and forward status are7388; mismatch index14 is
CR1b, expected05 and observed85. Fifteen checks were completed, so the preceding
11 MMIO and3 CRTC comparisons passed. Cleanup mask0 reports all20 saved-value
comparisons matched; selectors-restored is1. Native CR0/3/4 are4001003b/0/610.

This probe batches the safe-prefix writes and then checks them in the original
order. It adds no delay or sampling block. The source body matches kernel733
except the attempt namespace and native CPU guard. comparison001.json confirms
the same first mismatch, full expected/observed values, check count and cleanup
result as kernel733. Thus this prefix rejection is observed in both execution
contexts; it is not unique to native execution. Timing and internal device state
are not established as identical. Full CR1b bit7 semantics remain unresolved.

Original704 also writes CR22/CR33 before its checks. Those writes are omitted
here. Consequently this result does not identify708/709's full-mode failure or
justify masking bit7, replacing a predicate, clearing status or shipping a fix.
The current finding is a rejected exact readback, not failed cleanup or proof
that the requested mode cannot work.

One SITE was accepted at21:16:00.990940UTC. After photo capture, the user manually
power-cycled to UnleashX. Nine preparation reports were collected once with
identical double reads. The source, binaries and staged executable pins passed;
unrelated E-root/Application entries were unchanged. audit001 passed at
21:23:23.787101UTC. PCI/CRTC/sequencer, geometry and allocation plan match737.
Kernel pre-arm CPU remains a separate measurement; no native result was written
to disk. The last persisted phase was handoff_armed. This was not a Windows boot
or normal Windows shutdown.

No hook, owned process or VM remains. No new build, launch, transport or audit
failure occurred during collection. Preserve the earlier recorded whitespace
review failure in this kit. All738 and earlier runtimes are CLOSED; do not
relaunch, recollect or parent them. The original photo stays private.

Next work should resolve the access contracts behind original phase4 rather than
repeat the now-measured prefix. In particular, CR22 plane-dependent readback and
the CR1b exact-byte predicate still prevent admission of a full first-failure
capture. Retain732/CAPTURE-PLAN.md as the explicit admission requirements. Review
primary source evidence and the authored driver checks before preparing another
physical experiment. No new739 kit, launch or functional driver change exists.

## Retained preparation and validation

The native CPU admission requires CR0 masked with e0000001 to equal40000001,
CR3zero, entry/critical IFclear and PAEclear. The source-only737 handoff and
frontend reuse is bound to738's fresh ELF:15 relocations,10 absolute sites.
The result contains76 words;13 optical rows expose the selected fields without
masking or truncating expected/observed values.

Before launch,56 actual ELF cases,12 fresh diskless CPU fixtures,53 relocated
integration cases,76 full-framebuffer optical cases,20 nxdk page-builder cases,
372 nxdk ownership cases and131379 host ownership cases passed. All CPU fixtures
closed. Exact linked object/bridge/payload bytes and source freeze were verified.
Stage and remote readback passed at E/Applications/XWNMode738.

XBE SHA256:085e8ebf9f50bc04efc8af11e3838cb5769a7b8102a112c99d42f78eec3cfd89.
whitespace-review001 preserves two whitespace-only lines flagged in the executed
integration harness; frozen bytes were deliberately retained and the remaining
staged paths passed whitespace review. No hardware predicate was waived.
