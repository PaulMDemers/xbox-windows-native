# 663: separate entry and timed indication errors

This fresh diagnostic reports the existing entry/show return values more
precisely. It uses closed662 as pinned source only. The caller is unchanged apart
from diagnostic symbol names; native inspection/admission/sender, CPU predicate
classification, display capture, timed indication and polling latch are unchanged.
No additional hardware reads, relaxed guard or automatic retry is introduced.

The prior662 solid amber/held black result matched entry or timed-show failure,
not a CPU predicate. The independent661 equal red/off result matched CPU admission.
Both outcomes remain preserved separately.

## Persistent result codes

Observe after15seconds. For multicolor patterns, distinguish a dark gap from
continuous color alternation. Cyclic ordering has no absolute starting frame.

| Persistent pattern | Existing return classified |
| --- | --- |
| Solid amber | Nonzero entry-latch error; takes precedence over show error |
| Red, amber, green, dark gap | show658 returned1: delay failure |
| Red, amber, dark gap | show658 returned2: busy timeout |
| Green, amber, dark gap | show658 returned3: completion status error |
| Red, green, dark gap | show658 returned4: completion timeout |
| Red, amber, green without a dark gap | Other nonzero show return |

CPU codes are retained: even red/off CR0, even amber/off IF, continuous red/green
CPUID, continuous green/amber RAM, continuous red/amber ESP, even green/off
multiple predicates at the relevant stage. An early inspect predicate takes
precedence over late RAM/ESP while the BSS diagnostic mask retains all mismatches.

Other retained codes: one red slot/three off encoding failure; one green slot/
three off missing or inconsistent CPU context; one amber slot/three off other
admission; two amber slots/two off sender error; two green slots/two off incomplete
result; solid red unsafe cleanup; solid green three safe local completions only.
Nineteen complete LED cycles must be distinct under rotation. This proves code
distinction, not that a human observation resolves every color/duration.

Final-latch failure can retain an earlier pattern. Initial amber/off and timed
green/off are not final results. Preserve ambiguous observations. No raw BSS
status, exact CPU register value, timer value or faulty-CPU diagnosis follows
from a light alone. Any nonzero entry/show prevents the network call, unchanged.

## Validation and lifecycle

Source, binary and tests are pinned in build/host/compiled/review receipts. Host
tests cover predicate/result combinations and setup-error precedence. Linked
tests exercise actual caller/indication/latch instructions with raw IN/OUT and
native sender outputs modeled. They verify exact final SMC masks, unchanged
captured fields, entry busy/status/completion and show delay/busy/status/completion
failure paths. These are not physical NIC/DMA/timer qualification.

Use fresh C:/xwn663 and /E/Applications/XWNLatch663 paths, fresh packet identity,
180-second receiver and one20-second-bounded SITE. Verify permanent Xbox-only UDP
firewall rule and protected ordinary720p/startup/savedXBOX480 before launch.
No startup hook, Windows launch or automatic reset. Record the held LED/screen,
request manual recovery, collect once and audit retained files. Preserve all
failed attempts, immutable releases and Ftdisk49/Popup26 limitations.

## Qualified artifact

Source tree `d584ce0b50ddfd58f8e7efeda7155b9e57b2a167`; XBE SHA256 `635a6cc2eeb62430b22a9d0a391fc191d5ad12f4f5c2201be5149f4a5aed44b1`.
53,760 sanitizer combinations plus12 boundary conditions,31 exact-linked cases
and45 artifact reviews passed.20 native/display object sections unchanged.
The19 LED code cycles are distinct under rotation; physical legibility remains
an observation. Stage001 records exact readback. No physical result at preparation.
