#228 exact backend refusal discriminator

227 trace001 is closed with state4 refusal and zero downloaded surfaces/bytes.
Its normal CPU workload and cold integrity passed, but backend preservation did
not qualify. The diagnostic did not expose which unchanged predicate refused.

This new child adds an atomic reason field to the existing opt-in227 QOM report.
It preserves every queue, renderer, primitive, pending-work, extent, overlap and
deadline predicate. It does not authorize a GPU ownership transition or retire
references. The prioritized reason is a discriminator, not a complete census.

Reasons:1 queue,2 renderer lock,3 primitive,4 arrays,5 inline array,6 inline
elements,7 inline buffer,8 frontend framebuffer use,9 nop wait,10 flip wait,
11 context wait,12 flush pending,13 sync pending,14 extent,15 cached alias.
Zero means none assigned; it does not prove preservation. Actual nonzero dirty
surface/readback coverage remains required by unchanged audit gates.

Build001 compiled but was NEVER launched. Review found an inherited check/store
race: the reporter could publish timeout after the worker's state check, then
the worker could reopen admission and overwrite timeout. Build002 replaces
that sequence with a CAS claim from1/2 to transient7 before any halt restoration.
A timeout winner cannot be overwritten; an expired worker selects5. State7
contains only bounded atomic stores and no external call or new request. The
reporter cannot expire an already claimed publication. This fixes the race; it
does not relax any pre-work predicate or establish GPU ownership.

Build reconstructs exact227 build005 source from its manifest, adds only the
reason reporting and restores the five borrowed files. A new immutable211
emulator child uses the unchanged224 native payload and explicit existing
emulator wizard policy. No physical access, null-device policy or device merge.
One paused actual Cromwell exit boundary requests the opt-in operation. Timeout
or uncertain acceptance quarantines the guest; complete breakpoint teardown is
required. Ordinary/debugger/physical qualifications remain separate.
