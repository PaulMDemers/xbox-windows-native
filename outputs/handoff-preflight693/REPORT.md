# 693 separate physical target and reservation base — kernel preflight passed

The incoming1.6 passed the revised kernel preflight and returned to the dashboard.
All eight reports were read back twice identically. This proves the recorded
allocation/copy/cleanup operations, not native execution or Windows1.6 support.

## Address handling established on hardware

The source buffer occupied physical01f00000..02000000. The stub page occupied
01eff000..01f00000. The kernel again accepted a virtual request at01eff000 but
returned a64KiB reservation starting01ef0000. The original target is61440 bytes
into that reservation and its entire4096-byte page fits.

693 retains the original target and the returned allocation base as separate
values. It uses the original target for the low virtual copy and the original
high allocation pointer81eff000 for the physical stub copy. It uses the returned
reservation base only for ownership bounds and release. While paging is enabled,
virtual01eff000 maps to physical000ba000..000bb000, which is distinct from the
physical stub page01eff000. Both pages received the same1024-byte canary and both
3072-byte tails retained their guards. Source/stub/framebuffer physical ranges
and the target alias passed their non-overlap checks. No refusal bit was set.
The virtual reservation was successfully released; both contiguous buffers were
freed. The last record reports restart requested and complete; subsequent FTP
collection confirms dashboard return. No screen observation is claimed for693.

The kernel-rounded base observed in [692](../handoff-preflight692/REPORT.md)
is normal API behavior that the old unchecked wrapper must handle. [691's
compiled-wrapper models](../handoff-preflight691/legacy-audit002.json) show that
replacing the physical execution address with a changed returned base can cause
an unowned write. Together these provide a concrete candidate loader defect and
a physically tested allocation/copy strategy. They do not prove the exact cause
of689's failed native entry or historical boot intermittency. No ordinary loader
or functional driver has been patched or installed by this work.

## Validation and retained failures

Admission requires a successful, page-aligned, nonwrapping returned virtual range
of4096..65536 bytes below2GiB that contains the complete requested page. Short,
displaced, oversized and overlapping cases remain refused. The source/stub upper
bounds and physical range/continuity guards remain. The single runtime change
from692 is separate target/base handling plus this explicit containment contract;
it is not a blind acceptance of changed addresses.

Fresh sanitizer policy tests pass, including12285 unaligned mutations and each
possible page offset in a64KiB reservation.19 actual nxdk-object cases pass.
The first object harness stopped at its500-instruction ceiling before the valid
case returned; it is retained. Fresh002 uses a2000-instruction bound and counts
execution: the same valid case returns after550 instructions, maximum559 across
all19 cases. These tests do not execute kernel APIs or the native paging path.

One SITE request was accepted at00:54:25 UTC October27. No retry, hook, console C
access, SMBus transaction, CR0/CR3 change, CLI, native transition or ordinary
launcher change. SDK/kernel API calls have no application-enforced timeout.
Unrelated E/application entries and staged bytes matched; no whole-volume health
claim. All invoked fixtures and this runtime are CLOSED. No owned host process or
build lease remains. Hardware ticket retained; owned E files retained. Incoming
1.6 last verified at HDMI dashboard. Never rerun/recollect these closed runtimes.

Evidence: [build](build001.json), [sanitizers](host001.json),
[first object limit](object-review001.json), [counted cases](object-review002.json),
[review](review001.json), [launch](launch001.json), [collection](collection001.json),
[analysis](analysis001.json), [closure](closure001.json), [next](NEXT.md).
