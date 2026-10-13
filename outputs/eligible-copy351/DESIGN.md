# Eligible plan byte instrumentation351

This is an exact348 child with a new read-only escape0x58574439, version351,
128bytes. The original348 escape, snapshot, statistics and PDEV layout remain
unchanged. Existing reserved PDEV words8/9 now hold a saturating64-bit eligible
plan byte total; word10 is a separate sticky overflow/invalid-input error.
All accounting and snapshots use the existing owner semaphore. No new locking,
admission, memory access, copy, upload, cache, mapping or lifetime policy.

The already computed plan bytes count for both OFF result-2 and ON results0/1.
Ineligible result-1 contributes nothing. Invalid result/byte combinations set
the new error, never alter the copy result. The new packet retains words0..11
layout except version; words12/13 carry eligible bytes and14 the new error;
words15..31 stay zero. The old packet does not expose these new words.

The new validator requires exact eligible-byte equality in ON mode, fast plus
empty calls equal eligible calls, and zero fast calls/bytes in OFF. Both modes
need positive eligible coverage for each measured overlap interval. Overflow,
counter regression, impossible identities, reserved words and malformed or
misplaced transport refuse. Top-level requested bytes are not the denominator:
actual350 proved legitimate bitmap engine calls cover the remaining6036 bytes.
No percentage threshold or historical349 requalification is introduced.

The probe changes only escape/version/error validation and packet tags.
Operations, independent pixel/source/guard oracles, profiling, timing and
joined audio workload remain unchanged. Matched native builds differ only in
PRIMARY_COPY. Host accounting is actual compiled code under ASan/UBSan; owner
semaphore and guest execution are not supplied by that host test.
