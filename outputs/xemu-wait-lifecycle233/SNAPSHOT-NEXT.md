# Next new observer: publish a bounded journal from the worker

Never rerun/recollect closed233 trace001. First live read succeeded and captured
51 complete set/guest-ack cycles; the fixed second sample failed after20 read
attempts hit the one-second bound, each reporting PGRAPH lock busy. The first
sample is valid partial runtime evidence; the planned stopped handoff and
Windows workload never happened. No protocol or ownership PASS follows.

The getter holds BQL and tries FIFO then PGRAPH. It correctly refuses to block,
but a host synchronous reader is an unsuitable dependency for the next handoff
observer. Do not lengthen the bound/search for a favorable queue or bypass locks.
An actual BQL/worker deadlock was NOT diagnosed: the getter always released
acquired locks on failure. The measured failure is bounded PG-lock contention.

A NEW opt-in model should request ONE bounded journal publication by the owned
worker. Under the existing PGRAPH lock, copy the ring/count/current PG fields
into fixed resident snapshot storage. Do not read FIFO fields unless that same
caller actually owns FIFO; the copied producer rows already mark FIFO invalid.
Preserve guest acknowledgement rows' genuine dual-lock snapshots. Publish the
immutable copied tuple only with an ordered worker terminal state. Reader
timeout must withhold unfinished storage and never reset/reuse/overwrite the
accepted snapshot. No new guest emulated register/wait/error writes, and no
blocking monitor lock acquisition. Review the actual worker lock transitions
and BQL dependencies before patching, including timeout/late completion.

Host tests should use the exact compiled copy/publication helpers and actual
QEMU atomic headers with explicit adapters, racing timeout and worker completion
and checking ring ordering/wrap, missing boundaries and FIFO validity. Retain
all failures. One fresh stopped-CPU preservation request remains separate from
ordinary live guest IRQ processing; never resume a producer inside that request
or clear NOP waits to force an empty queue. A guest-side producer-close/quiesce
boundary and independently retired backend/frontend references remain needed.

Require owned cleanup, fresh cold allocation/hives/protected hashes/events and
unchanged device policy. If Windows never launched, record CPU/shutdown scope
false and do not waive it. Root first-boot/dashboard audits do not qualify USB's
independent repeated-boot stale-sector failure (32f8217). No physical deploy,
device merge, native grant, release tag change or all-file-content claim.
