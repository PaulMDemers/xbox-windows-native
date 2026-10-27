#728 closed: minimal interaction also returns85 under the Xbox kernel

One SITE accepted2026-10-27T19:02:21.122652+00:00. User observed green and
an automatic return to UnleashX. Seven exclusive reports were collected once,
double-read and audited against source/build/stage pins. Audit001 passed.

| Observation | Native727 | Kernel728 |
|---|---|---|
| Baseline630/CR1b |3/85|3/85|
| After6302/unlock, beforeCR1b write |2/85|2/85|
| Direct / reselected read after oneCR1b05 |05/05|05/05|
| First sample after saved6303 |3/85|3/05|
| After gate4 andSEQ1 restoration |3/85|3/85|
| Last of32 late samples |3/85|3/85|
| Late changes |0|0|
| Full baseline/selectors |pass|pass|

Numbers above are hexadecimal except sample/count values.728 code728,
attempts630=2,unlock=1,CR1b=1. All three preserved CR11/22/19 values match.
Actual probe CR0=80010031,CR3=f000,CR4=610; EFLAGS246->046->246. Separate
pre-file context was flags286/CR08001003b/CR3f000/CR4610,CS8/DS16/SS16.
No native handoff or control-register write occurred. Preparation PCI, CRTC,
SEQ, geometry and framebuffer match retained723/727 exactly.

This rules out a simple claim that the minimal sequence can return85 only
in native context. The first observed transition occurs at different sample
boundaries. Timing, intervening output writes and context remain unresolved;
no register bit semantics, full modesetting repair or Windows support proved.
Kernel723 used a larger prefix and retained05, so it is not a matched control.

Comparison001's broad model-vector comparison was false: physical unlock1f
returned03, while the inherited model returned57. Comparison002 preserves that
mismatch and separately verifies the stage/direct/late progression. This field
is recorded but is not an admission predicate; no candidate changes or waivers.
Model names describe simulated behavior, not a demonstrated physical mechanism.

Initial preparation parse failure retained; build/compiled models/staging,
launch, collection and audit passed. No manual reset, hook, owned process or
VM remains. Automatic firmware return is not normal Windows shutdown.728 is
CLOSED; do not relaunch or recollect. See NEXT.md for the fresh bounded probe.
