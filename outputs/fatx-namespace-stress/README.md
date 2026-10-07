# Held before launch

Candidate0100 and this prepared fixture were never launched. The0099 repeat
captured a parent-directory cache-flush cycle that0100's regular-file ordering
does not fix. The corrected five-worker helper is reused unchanged by
`../fatx-directory-order`; that candidate separates directory-stream ordering.
Do not launch this superseded fixture.

# Five-worker namespace/flush stress for0100

The original two write/flush/close workers and volume-flush worker run500 rounds
each. Two additional simultaneous workers perform500 metadata/rename cycles and
500 complete directory enumerations. Metadata cycles create/write a separate
file, truncate to1025, extend to4097, rewrite exact data, flush/close, toggle
read-only/archive attributes, and rename with replacement. No raw-volume I/O or
volume lock/dismount is requested. This is synthetic API coverage, not Paint UI.

Cold qualification requires all five counters500, zero errors, three exact
final files and absent meta.tmp, ordinary restart, unchanged driver/video/kernel
payloads, five structural hives and a consistent full allocation audit. The
helper timeout is600s, host deadline900s and owned runner limit1200s. An initial
unlaunched build inherited the wait-all result bug; its bytes/source/metadata
were retained privately, and the reviewed replacement accepts only the documented
success range0..4. Timeout/abandonment/failure still fail, and the pending-install
guard remains exactly WAIT_OBJECT_0.

Candidate0100 is an emulator-only sibling of the same settled null-INF parent.
Inherited audio failed-install flags and historical physical event failures are
not waived. All snapshots remain private; preserve the installed physical
FATX0098/video0093 and0.1.0 until independent hardware qualification.
