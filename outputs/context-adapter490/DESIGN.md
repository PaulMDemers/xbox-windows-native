# Read-only CPU context adapter

This new diagnostic starts from exact487. Its normal loader, payload, thunk
imports and original saved handoff frame remain unchanged. Byte-identical489
capture reads privileged CPU registers only. It does not walk page tables or
dereference descriptor tables. No physical-memory mirror is assumed.

Epoch1 is taken at witness entry, before the original witness preparation and IO.
Epoch2 is taken after that witness's successful close, before the NEW context file
is opened. The saved400-byte packet contains both160-byte snapshots, explicit
boundary IDs, the actual preceding close state, witness address and original
saved-frame address. The capture's return EIP and ESP identify its adapter call,
not the original handoff EIP/ESP; the latter remain in the original witness.

A synchronous claim advances0->1->2, never resets. Slots start fresh and each is
captured once. This is not an asynchronous multi-thread publication protocol.
Each shim preserves the entry flags until capture, while the original handoff
frame remains untouched. Snapshot equality does not exclude intermediate changes
and restoration. Nonserialized TSC samples are observations, not timing proof.

The context file is exclusively created in a new owned directory. Pending status,
nonzero return/IOSB status, wrong creation disposition or byte count, null handle,
flush failure or close failure refuses. Reasons20/21 identify pre/post capture
admission;22..25 identify context create/write/flush/close. Existing13..19 witness
reasons keep their meaning. The actual original refusal path handles cleanup.
No file call is retried. Original final payload/high/low comparisons run AFTER
the new context file close, before the original saved frame is restored.

The persisted packet proves neither its own final IO completion nor later
comparisons, CLI, paging transition, Xromwell or Windows execution. A partial or
absent packet remains partial/absent evidence. Kernel IO has no individual
cancellation guarantee; physical runs retain an outer observation bound.

Host qualification will execute the actual adapter, capture and original witness
instructions in an owned diskless privileged CPU fixture. Synthetic kernel IO,
allocation contents, CPU state and refusal endpoint are explicitly modeled.
Fault cases must retain the first failing lifecycle reason and never reach the
handoff endpoint. Original inputs and failed cases remain immutable. This is
diagnostic instrumentation, not a functional fix or ordinary boot qualification.
