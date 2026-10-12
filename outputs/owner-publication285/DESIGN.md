# Publication boundaries and limitations

States: armed0 unused,1 initializing,2 ready,3 initialization refused. The single
gate word carries busy1, closed2, contention4 and foreign8. Entry can acquire BUSY
only while open. Foreign/busy errors linearize via CAS on the same gate; once
closed, they can neither enter nor change published errors. The owner and core
are visible after acquire-ready. Exactly one caller claims sealing.

Seal atomically closes entry. If BUSY was present, terminal3 is a refusal without
touching the concurrently owned core; retain the whole object until normal owner
teardown is independently established. No retry is permitted after that failure.
Otherwise the original owner seals284, writes the entire envelope/core bytes,
then release-publishes terminal2(success) or4(encoded failure). Getters require
acquired2 and enough capacity before copying. An acquire of CLOSED is never used
as a substitute for the terminal publication. No mutable successful record.

Envelope: eight LE64 fields magic/version/5504/owner/gate/gate-errors/core-errors/
serialized, then byte-identical5440byte284 core. The independent decoder takes
the independently attested expected owner, old keys, identities and names. The
future controller must join actual context/CPU/graph, snapshot and file transport
errors with this envelope. This prototype does not implement those providers.

Callers must keep all callback entry/core mutation/leave paths balanced. Foreign
owner IDs in tests are models, not OS-thread authentication. Actual integration
must source identity from the pinned renderer thread API and verify owner/context
at all worker boundaries. No manual host calls may manufacture lifetime events.
File publication must be exclusive, bounded, one-shot and separately acknowledged;
the memory record alone does not prove a file or actual GPU completion.

Do not use this prototype to change old269/273 semantics or reset their actors.
No callback removal, global flush, reset, join, pending clear, event suppression,
native GPU handoff or speculative functional driver change is included.
