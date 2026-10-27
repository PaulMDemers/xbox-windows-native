# Native CR1b/630 interaction control727

Closed726 retained CR1b85 while630 changed3->2->3 without CR1b writes. Closed725
observed05 after its explicitCR1b05 write, then85 after630 restoration in a larger
prefix. This new control isolates the combination with no other prefix data writes.

After the retained native/framebuffer admission and output blanking, it writes
6302, performs the established unlock1f57, verifies the prewrite context, and
writes CR1b05 exactly once. It reads the data port immediately, then reads again
after reselecting1b. It restores saved6303 once and restores output. Thirty-two
bounded late pairs record whether CR1b changes again. No repeatedCR1b write,
repair loop, guessed writable mask, CR19/CR22 or encoder/timing programming.

Full-width630 and full-byteCR1b final baseline checks remain. Green requires
immediate direct/indexed05 plus final baseline85 and other restoration checks.
Orange means refusal, mismatch or cleanup failure. A retained05 final value is
reported as failed baseline restoration; it is not silently accepted or masked.
Neither color alone proves coupling or bit7 semantics. Decode the raw photo.

The13-row schema in optical-schema001.json exports signature, bridge phase,
admission, return code, packed attempt counts, baseline pair, post-unlock
prewrite pair, packed direct/indexedCR1b reads, post6303/output/late pairs, late
change count and summary. Pairs use high16 for630 and the low byte forCR1b only
when630 fits. Otherwise ffffffff is unrepresentable/unreached; full-width checks
still apply. Direct read occupies high16; indexed read the low byte. Intermediate
blanking/after6302 and late min/max remain in RAM and are not exported. Samples
are sequential rather than atomic, and added accesses affect timing.

Fresh validation passed:12 diskless CPU cases (all VMs closed),50 integration
cases,76 whole-framebuffer optical cases,20 nxdk page-builder cases,372 nxdk
ownership cases and131379 host ownership cases. The integration model enforces
write scope/count/order and the direct-read/reselect/read sequence. Independent
models cover reassertion at6303, retained05, output/late restoration, oscillation,
ignored writes, direct/indexed differences, prewrite refusal and cleanup failures.
These are instrumentation/guard tests, not physical hardware semantics.

Source, compiler, SDK, relocation, page and linked PE/XBE pins passed. Seven ELF
relocations include one absolute relocation. Result216bytes fits the owned slot.
Active scripts: payload_build.py; host_build002.py; cpu002.py; integration003.py;
optical_review002.py; build003.py; page_review002.py; plan_review002.py;
linked_review002.py; source_review.py; review_prepare.py. Use the existing leases.
No build/test failure in727 preparation; earlier failed evidence stays unchanged.

Staged/read back only /E/Applications/XWNMode727. No launch yet; readiness pending.
No startup hook, ordinary launcher/720p change, Windows launch or dashboardC access.
Private binaries/configuration remain underC:/xwn727; public files are authored
source and evidence only. See NEXT.md. Never reuse a closed runtime.
