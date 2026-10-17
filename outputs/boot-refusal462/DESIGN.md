# Preserve first deliberate wrapper refusal

Exact461 child with separate462 identity. On every existing refusal path, snapshot
first reason/status/IOSB/handle/close-attempt state and the earlier copy evidence
BEFORE cleanup changes them. One exclusive96-byte refusal.bin write is attempted,
with separate handle/IOSB. No recursion, retry, rollback or handoff after refusal.
No fallback I/O on the successful path; saved jump registers/flags still restored.
No Xbox kernel/file calls after paging. Original installed launcher unchanged.

Reasons1..11: create, header write, header flush, trailer write, trailer flush,
close, missing snapshot, ineligible original copies, post-log payload, high loader,
low loader. Closed-state0=not attempted,1=attempted/failed,2=success. Status fields
are raw; IOSB belongs to the most recent primary I/O and is not a close status.
Cleanup-close status is0xeeeeeeee when skipped. Capacity96 fixed; magicR462,v1,
cookie46200101, DONE trailer. First failure remains immutable during fallback.

A complete fallback record proves reaching a refusal, not successful fallback
flush/close or actual reboot. Missing fallback bytes remain UNKNOWN. Faults before
this handler, hangs inside kernel calls and later boot failures need separate
observation. Individual kernel calls lack an independent cancellation guarantee.
All primary/secondary failure modes need actual assembled-wrapper host coverage
before one unique physical attempt; kernel/file effects are host models.

The refusal reason identifies the first failing logging/final-check branch.
An earlier allocation/mapping/copy refusal may already be represented by the
separate preparation phase. Both are retained; a subsequent file error does not
replace that earlier preparation evidence or establish the original boot cause.
