#726 CLOSED: 630-only transition retains CR1b85

One accepted launch18:13:46UTC2026-10-27. Green held result/photo001:
7260000d,4,5,726,2,30085,30085,20085,30085,30085,30085,0,22007.
6303->2->3; CR1b85 throughout six displayed stages and zero changes in32
late pairs. Two writes and final cleanup/selectors pass; no CRTC data writes.

User power-cycled. Collected nine preparation records once/double-read;
audit001 passed exact sources/binaries/photo, allocation/alias bounds and
unrelated E entries. PCI/CRTC/SEQ/geometry/allocation preparation matches725.
Last file phase handoff_armed; native values are optical only. Manual reset
is not normal Windows shutdown. Console UnleashX; no hook/process/VM.
Preserve integration001 harness expectation failure. Runtime726 CLOSED.

NEXT outputs/native-630726/NEXT.md: fresh minimal interaction control combining
6302, oneCR1b05 write and saved6303 restoration, with raw stage samples.
No new build/staging/launch. Do not reopen726/older runtimes or infer bit7
semantics, a full-mode fix or Windows qualification. Ordinary720p protected.

#726 PHOTO VERIFIED: 630-only transition leaves CR1b85

One accepted launch; user green held picture. Photo001 independently decodes:
7260000d,4,5,726,2,30085,30085,20085,30085,30085,30085,0,22007.
6303->2->3; CR1b85 at all six sampled stages; zero changes in32 late pairs;
two writes, final cleanup and selectors pass. Constant model matches.

This control leaves CR1b unwritten and does not reproduce725's05->85 change.
It does not exclude an interaction with explicitCR1b05 or the other prefix
writes. No bit7 mask, full-mode/Windows or acceleration qualification.

Console holding; user power cycle requested, Ready pending. No new launch,
collection, hook, owned process or VM. Next: after Ready collect726 once with
physical.py, then audit_collection.py. Photo stays private underC:/xwn726.
Closed725 and earlier runtimes stay closed. Ordinary720p remains protected.

#726 LAUNCHED: green held result, photo pending

One SITE accepted 2026-10-27T18:13:46.296106+00:00 after user watch/reset
readiness and exact local/remote byte verification. User reports Green, holding.
Green reports control completion and final restoration; intermediate CR1b
behavior remains unknown until the13 optical rows are decoded. No repeat launch.

Leave console holding for full report photo. Then decode independently before
requesting power cycle. Only after Ready at dashboard, collect this attempt once.
No hook/owned host process/VM. Preparation commit4bf6b99b; closed725 remains closed.
No full-mode/Windows/acceleration claim. NEXT outputs/native-630726/NEXT.md.

# Native 630-only control 726

Probe725 first observed CR1b changing from 05 to 85 after restoring register
0x680630 from 2 to 3. This brackets a boundary; it does not establish causality.
This fresh control removes the other setup writes and leaves CR1b entirely
unwritten. It is a diagnostic, not a video-driver fix or a complete mode change.

The native payload admits the existing 720p framebuffer and baseline context,
blanks output, writes 630=2 once, restores its saved value 3 once, and restores
output. It samples 630 and CR1b before blanking, after blanking, after each write,
after restoring output, and in 32 bounded later pairs. Samples are sequential,
not atomic. Full-width 630 and full-byte CR1b final restoration checks remain.
CR11/CR22/CR19, SEQ1 and selectors are checked; there are no CRTC data writes.

The green top bar marks the native handoff. A green second bar means the control
completed and restored its final baseline; it does not select a coupling theory.
Orange means a check failed. The 13-row optical report is specified in
optical-schema001.json. A pair packs 630 into the high16 bits and CR1b into the
low byte only when the full 630 value fits; ffffffff means unreached or overflow.
The raw full-width value still controls admission and restoration checks.

Validation: fresh payload and bridge, 12 diskless CPU cases (all VMs closed),
44 integration cases, 76 whole-framebuffer optical cases, 20 nxdk page-builder
cases, 372 nxdk ownership cases and 131379 host ownership cases passed.
Integration models cover constant CR1b, coupling, blanking-only changes, delayed
return, later oscillation, dropped/wide writes, cleanup failures and refusals.
These validate instrumentation and guards, not physical register semantics.

Preserve integration001.json: its harness expected a CR19 low-bit mutation to
fail the outer pitch check. That bit is excluded there; the payload correctly
refused it at its own baseline. Fresh integration003.py / integration002.json
corrected the expectation without changing the binary. See lineage001.json for
source references and the descriptive-only payload harness clarification.

Active build: payload_build_executed.py, host_build002.py, cpu002.py,
integration003.py, optical_review002.py, build003.py, page_review002.py,
plan_review002.py, linked_review002.py, source_review.py, review_prepare.py.
Commands require the existing build/emulator leases. Receipts pin commands,
tools, private paths and bytes; do not rerun an existing attempt directory.
Authored sources only are public. Private binaries/configuration live under
C:/xwn726. No closed runtime is reused or parented.

Staged and read back at /E/Applications/XWNMode726. No launch yet. No startup
hook, ordinary launcher change, Windows launch or dashboard C access.
See NEXT.md for the exact next action; readiness is pending.
