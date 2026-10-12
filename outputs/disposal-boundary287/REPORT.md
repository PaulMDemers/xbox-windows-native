#287 — explicit four-boundary scalar contract, host-only

No actual collector/provider/worker, renderer/native build, guest preparation or
launch. No cache disposal installed and no physical change. This is the contract
needed before composing283 disposal with284/285/286 observation in a new runtime.

Four distinct states are modeled: original unit+cache owners; cache-only after
unit release; candidate old cache owners absent before guest resume (control
retains cache-only owners); and normal guest replacements/rebinds. Historical
anchors remain separate from current objects. Candidate absence requires every
current object/key field zero, a completed-free record and namespace-deletion
evidence. Stage4 requires distinct generations5..8, while addresses/GL names may
legitimately recycle. Both modes retain exact keys and4096byte allocation guards.

The common CPU/callback/surface validation prefix comes exactly from280 except
the new function signature and explicit stage bound1..4; epochs are1..8. Old
280/277 code is untouched. The obsolete textures array in that shared scalar
header must be zero; selected current/historical state lives in the new structure.
No fabricated refs2 or fake epochs are passed to an old validator.

Host003 ASan/UBSan passes596 checks across both modes and all four stages. Tests
reject incomplete/mislinked proofs, ghost owners at the absent stage, old
generations as replacements, wrong counts/keys/guards, callback ABA clocks,
invalid namespace widths and changing immutable anchors. Clocks must stay equal
through the first three boundaries and may increase, but never decrease, after
real guest work. Actual source collection/transport is NOT provided here.

Host001 passed its initial594 checks. Host002 added a decreasing-resume-clock
case and FAILED: the proposed chain check had accepted that invalid state.003
adds the monotonic rule, explicit32bit GL-name bounds and a self-contained bool
include. The test harness now mutates struct fields through memcpy, avoiding
pointer-arithmetic assumptions across member objects.001/002 inputs/results are
preserved; no historical runtime result is changed or retroactively qualified.

All CPU/GL/full-graph/namespace values are supplied HOST MODELS. In particular,
inventory_complete and old_gl_deleted are requirements for a future independently
reviewed actual provider, not evidence that an inventory or deletion happened.
No full retirement, acceleration, native Windows GPU grant or physical promotion.
