# Locate the token close within the observed validity interval

175 proves01B4 token1864 query class12 succeeds before inner creation; after
innerTRUE, query class8 fails STATUS_INVALID_HANDLE and outerFALSE/error6. No
same-thread supplied-token close was captured; other threads' native API hits
were excluded. Popup producer remains separate/unresolved; no fix inferred.

New176 changes observation only: while services outer creation is active, allow
user NtClose and actual runtime-kernel NtClose from another thread when handle
AND owner EPROCESS pointer match the active token scope. Keep every excluded hit;
do not mistake equal numeric values in another process's handle table for a close.
No global close tracking, guest-data/register change or forced paging. A thread
attached to another process may require separate handle-context evidence; do not
claim its owner EPROCESS always equals active handle-table context. Ambiguous
active token scopes refuse capture. Read-only selector tested positive/foreign/
wronghandle/empty/ambiguous cases; same identity/32unreadable/1024hit/360sec gates.

Derive kernel close breakpoint ONLY after actual IDT/image discovery, then arm
only within outer call. User/kernel close entry/return pairs use exact ETHREAD/
stdcall delta; retain successful status/caller/outer interval. No interpretation
of unrelated hits at a shared kernel syscall return as our pending return. Record
and exclude foreign thread/frame hits; only exact pairs count, and incomplete
pending pairs make capture incomplete. Original pre-return-selector source/tests
retained; current exact-source identity/close/return-selector tests required.
No interpretation
of cleanup status as cause. Fresh162candidate, same112/v4/166runner/drivers/hives/
settings/pending devices. Full breakpoint teardown/resume, normalshutdown/dashboard
and cold pixel/coherence/allocation/5hive/protected/event gates unchanged. Never
retry173/174/175; debugger ONLY, no ordinary/performance/physical qualification,
physicalFTP/deploy/test or event waiver. Preserve physical baseline/rollback/0.1.0.
