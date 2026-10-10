# Next: separate boot-video writes from observed GPU backing

physical64-analysis.json establishes exact passive content correspondence between
PRAMIN fd710000..fd715000 and CPU physical03feb000..03ff0000, reversing64-byte
block order. The allocator query supplies end83ff0000/padding10000. This covers
one64MiB stock4034 boot, not arbitrary kernel versions,128MiB consoles or a write
capability. Preserve query-only payload/result as frozen evidence.

The pinned boot provider in ../video-gpu-transfer-contract212/artifacts/boot-reservation
places its316160-byte indexed backing at03fb2d00..04000000. VidResetDisplay also
calls RtlZeroMemory(FrameBufferStart,0x400000). Both write domains include the
observed instance window. This is a source/range hazard; this run never booted
NT5 and does not observe a Windows-induced GPU collision.

Proposed64MiB layout, all ranges half-open:

| Use | Physical range | Bytes |
| --- | --- | ---: |
| Permanent UC mapped reservation | 03c00000..04000000 | 4194304 |
| Proposed boot-video writable domain | 03c00000..03feb000 | 4108288 |
| Proposed indexed backing | 03f9dd00..03feb000 | 316160 |
| Observed instance window | 03feb000..03ff0000 | 20480 |
| Query padding, retained untouched | 03ff0000..04000000 | 65536 |

HiddenOffset becomes0039dd00. The current640x480x4 visible area fits below that
boundary; every actual stride/height must be checked before mapping/publication.
Do not claim1920x1080 fits, or enable modes from this layout arithmetic. Keep the
4MiB permanent crash mapping/reservation; changing mapped/reserved length would
change shared-provider ABI and allocator protection unnecessarily.

Create a NEW immutable child from the verified boot-provider source. Review all
reset/initialization/bitmap/panning/preserved-row writes and every published-view
consumer. Change capacity validation, reset clearing, indexed-buffer placement
and HiddenOffset together. Check overflow before subtracting the0x15000 tail.
Unsupported profiles must not obtain a GPU capability based on the64MiB result.
Publish an explicit writable boundary before any future command allocation.

Validation must include independent guards at the new indexed end and protected
tail, boot/reset/crash rendering geometry, actual published HiddenOffset and
runtime backing hashes around each write phase. Guard hashes prove a specific
write interval survived; they do not release firmware channels. Use separate
normal control/candidate cold audits, retained originals, unchanged strict events
and full teardown. xemu's separate RAMIN remains an explicit physical gap.

Only after that layout is qualified, acquire/service/drain a single bounded
software-switched context using the216 observed state. Require sequence-matched
completion, timeout/quarantine and crash/ownership fencing. Then attempt one
guarded16x8 off-screen copy; modes and desktop acceleration follow that result.
No new source tree, Windows driver build/deployment or GPU store occurred218.
