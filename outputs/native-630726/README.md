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
