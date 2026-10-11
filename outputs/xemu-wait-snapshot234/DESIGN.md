#234 one-shot worker journal publication

Fresh child of selected233 build002; all failed233 records stay closed.
The live monitor setter only try-locks FIFO to release-publish ONE request and
wake the existing worker. It changes no guest register, halt, wait or IRQ state.
The GL pending worker claims request1->2 while already holding FIFO, releases
FIFO BEFORE PG acquisition, copies at most256 chronological rows and a current
PG-only row into resident fixed storage, releases PG, publishes, then reacquires
FIFO. There is no BQL acquisition or FIFO acquisition under PG in this hook.

States0 unused/1 requested/2 copying/7 publication claimed/3 immutable/5 timeout.
Deadline5sec QEMU_REALTIME; only1/2 expire. CAS2->7 claims completion after the
copy and predeadline check; release3 exposes every copied byte. Reader acquire3
is required to report any tuple or rows. A reader/worker timeout winner hides
late storage forever; no reset, repeated request or snapshot reuse. A copy
already in flight may finish privately after timeout but cannot publish.
Tests retain the exact compiled helpers and QEMU atomic headers with explicit
clock, object, string, register and mutex adapters; they do not test QEMU GPU
scheduling or hardware memory visibility.

Copied producer rows remain FIFO-invalid; actual dual-lock guest INTR/reset
rows retain FIFO-valid data. The worker current row is FIFO-invalid/zero.
The live snapshot is immutable: reads after CPU stop/preservation are the SAME
old live tuple, never a contemporaneous stopped PG/FIFO observation. Actual232
request/gate tuples and wait-before/after remain the separate stopped diagnostic.
No native ownership, producer-close, reference retirement or empty-queue search.
One fresh attempt, normal safety quarantine and complete owned closure/cold
audits; failed publication aborts before Windows. Existing211 explicit wizard
policy, no synthetic null devices; physical baseline/releases untouched.
