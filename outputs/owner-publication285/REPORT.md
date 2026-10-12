#285 — owner/seal publication prototype, host-only

No renderer/native build, guest preparation/launch, installed hooks/disposal or
physical change.282 remains the latest actual renderer result.284 core/decoder
are byte-identical inputs; neither previous qualifier nor failure is rewritten.

A one-word atomic entry gate combines BUSY/CLOSED and refusal bits. Error updates
use CAS only while open, so a rejected call linearized after closure cannot
change an immutable terminal. A distinct acquire/release terminal publication
protects the bytes; a closed gate alone is insufficient. Sealing is one-shot. If
an in-flight callback exists, the gate closes, terminal state becomes quarantine,
and no core read, encoding, retry or metadata free occurs. The callback may leave
normally and its storage must remain alive. No wait, join or forced completion.

Host002 ASan/UBSan passes2048 reader/publication cases,2048 held-callback seal
quarantines,4096 foreign-caller/seal races,4096 entry/seal races,20000 closed
foreign refusals and11008 undersized reads with destination bytes unchanged.
The separate5504byte envelope includes closed gate/refusal/core state; independent
decoder rejects169 altered/failed/truncated records. Failed unions never expose
a successful read. Host001's original passing subset is preserved. Publication
code and decoder are byte-identical001/002;002 only adds concurrency cases.

Owner IDs and lifecycle callbacks are explicitly supplied HOST MODELS. Pthreads
exercise the proposed actual atomic code, but no actual QEMU worker identity,
dispatcher, GL operation, snapshot/file publication or guest result is proved.
No ThreadSanitizer claim; this used ASan/UBSan and explicit concurrency assertions.

The stable-lifetime zero-initialized object has no reset/free API. Arm publishes
initialization before allowing entry. Normal terminal is sealed only on the
acknowledged owner in a future adapter; foreign seal attempts refuse. Negative
records are preserved; the core decoder remains284 and273 remains untouched.

Actual completed-destruction, creation and normal-bind hooks plus the complete
four-boundary proof provider are still required. No acceleration or GPU grant.
