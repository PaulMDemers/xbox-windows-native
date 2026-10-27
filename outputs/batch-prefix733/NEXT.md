# 733 CLOSED: first deferred mismatch is CR1b05 versus85

Read REPORT.md, audit001.json and comparison001.json. All15 writes attempted;
first14 checks pass, CR1b expected05/observed85 before recovery.680630 checked2.
Full cleanup and selectors/flags restored; user orange/automatic dashboard.
No CR22/CR33 data writes, native handoff or full-mode replay. No hook/process/VM.
Console last seen UnleashX. Never rerun/recollect/parent733/732/731/prior runtimes.

Next: review the CR1b FIFO-control access contract and the unchanged original
predicate using this concrete first-mismatch evidence. An85 read is now observed
without680630 restoration; don't keep attributing the transition solely to the
2-to3 restore. Different runs/read schedules are not an elapsed-time proof.
Retain the raw full-byte rejection and determine independently which fields can
be verified after programming. No guessed bit7 mask, pending-bit clear or extra
CR1b write. If another probe is justified, use a fresh bounded design that can
distinguish register semantics; no identical prefix/full-boot repeat.

CR22 read-plane dependence and unknown CR22/CR33 write effects remain separate.
Any corrected driver predicate needs primary-source/access evidence and negative
validation, followed by new physical qualification. No functional patch, native
mode switching, Windows1.6 or acceleration promotion from this result alone.
