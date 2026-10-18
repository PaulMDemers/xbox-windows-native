488 is closed. Do not rerun lab001..003 or any earlier physical/emulator attempt.
No new console test is queued and no hardware response is required now.

Next build a NEW bounded read-only pre-transition CPU-context diagnostic on the
exact487 wrapper, before choosing a functional handoff change. Capture actual
CR0/CR3/CR4, selector values and descriptor-table registers; validate actual
mapping/permissions/cache attributes for both loader copies and payload with a
bounded page-walk provider. Independently verify the provider's memory access
contract against the pinned Xbox kernel before dereferencing physical mirrors.
Do not infer flat segment bases from selectors, or actual tables from
MmGetPhysicalAddress alone. Refuse unsupported modes/ranges and incomplete captures.

Keep initial and final context epochs distinct. A receipt written before final
flush/close/comparisons cannot attest those operations or later context. Preserve
the original frame and loader bytes. Host-test actual capture instructions,
serialization and refusal paths in the diskless fixture before integrating a
fresh XBE. Any new memory, I/O or instrumentation perturbs execution and must be
explicit. Do not amend487, silently add an identity mapping, clear interrupts or
rewrite page tables as an observational diagnostic. If a later matched functional
candidate is justified, give it a separate contract and unique control/candidate.

Alternative post-PG instrumentation needs a stackless bounded design until the
original payload installs ESP; no kernel file calls after paging is removed.
Existing464/466/470/471 marker work is relevant and must not be reinvented or
reused as proof of physical execution without actual records/user observation.
Never borrow firmware state for persistence or infer missing marker = failed entry.

After reviewed diagnostic coverage, one fresh matched Xbox486 arithmetic attempt
can follow with the same independent oracle and owned one-shot startup. Preserve
484 exact-endpoint failure,486 characterization and487 no-result failure. Then
continue to windowed D3D presentation. No boot stability, GPU or game claim yet.
