# 729 closed: CR1b returned to 85 before output restoration

One accepted launch at 2026-10-27T19:10:45.887391+00:00. The user observed
GREEN and an automatic return to UnleashX. Seven reports collected once,
double-read, and audited against source/build/stage pins. Audit001 passed.

| Sample | Full 630 | Full CR1b |
|---|---|---|
| Baseline | 3 | 85 |
| Before the single CR1b05 write | 2 | 85 |
| Direct / reselected read after write | 2 | 05 / 05 |
| First sample after saved6303 | 3 | 05 |
| First extra sample, still blank | 3 | 85 |
| All 32 extra samples, still blank | 3 | 85 |
| After gate4, before SEQ1 restore | 3 | 85 |
| After SEQ1 restore and 32 late samples | 3 | 85 |

Register values are hexadecimal. At the intermediate gate sample, SEQ1 was
21. The blank counter reports 32 samples and one change from the original
post630 sample; min05/max85. No late changes. Full baseline and selector checks
passed. Two630 writes, one unlock request and oneCR1b write; no extra data writes.

In this attempt the transition occurred before gate4 and SEQ1 restoration, so
those writes were unnecessary for the observed transition. This is not proof
of elapsed-time-only behavior: selector/read effects and delayed updates remain
unresolved. No timing measurement or new writable-bit interpretation is claimed.

Preparation PCI/CRTC/SEQ/geometry/framebuffer matches728. The first54 result
words differ from728 only in the attempt code and actual CR0:729=8001003b,
728=80010031 (xor0a). Both had CR3f000/CR4610 and EFLAGS246->046->246. CPU
contexts were not identical and this difference is not assigned causality.
The separate pre-file context remains separately recorded. All sample fields
20..124 match the independent blank-delay-1 model, which is not mechanism proof.

This resolves the immediate output-restoration question raised by728. It does
not locate708/709's full-mode failure. Native724/725 already covered immediate
pre-CR22 prefix readbacks; their cleanup85 observation must remain recorded,
not retroactively converted into a pass. Return to the next uncovered setup
boundary with source review first; see NEXT.md. No driver change or Windows1.6
qualification follows from this probe.

No729 build, launch, collection or audit failure. Automatic firmware return is
not normal Windows shutdown. Console at UnleashX; no hook, owned process or VM.
729 CLOSED: never relaunch, recollect or parent this runtime.
