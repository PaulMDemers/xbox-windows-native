# 128GiB dump-address defect: emulator closure

Candidate0105 fixes the observed crash-only address truncation in the pinned
Windows2000 ATAPI driver. The ordinary path already selected extended ATA;
the dump path called the legacy routine directly and discarded the high nibble.
EnableBigLba was already1 and the actual device advertised48-bit support.
The original failure wrote at intended offset minus2^37 while reporting success.
The evidence-driven correction selects the driver's existing extended PIO routine
for supported requests and rejects unsafe legacy or malformed ranges.

Validation is complete for the owned250GB emulator fixture:

- 4480 actual selector instruction tests: ABI, address bounds, capability routing,
 overflow/malformed rejection and no memory writes.
- Matched fresh ordinary control/candidate: both strictPASS for792 appends,
 32 allocation shrinks,132 reopens,11 exact files, bounded bidirectional TCP,
 normal shutdown, full allocation, five hives and clean event deltas.
- Controlled crash006: correct command39 at148440145920, all65,536 persisted bytes
 exactly equal captured write buffers, old alias unchanged and all observed
 dump writes contained in the intended extent.
- Separate recovery003: Windows saved the exact same64KiB dump and restarted
 normally; independent Microsoft debugger parsed its header, identity, context
 and modules. Allocation/hives/protected files/event deltas passed.

Candidate SHA256:
409c4de7313fe8889b6d2f7208616b06c70596db8720a657b4ed2f60fd838de1.
Preserved source input SHA256:
faf9639ac8d14e9c72a4a2d7b8d3a6ceb9965f8bbc79c77d89a45733d745c675.
Reproduction requires that exact privately owned input; build.py verifies it,
build-helper.sh assembles the105-byte selector, and test-dispatch.py executes it.
No vendor binary is committed or redistributed. See DESIGN.md/build-review.json
for the minimal old-instruction change and PE layout checks.

This is bounded emulator qualification, not physical qualification. Scope is
512-byte-sector WRITE(10) within the upstream32-bit sector-address limit; it
is not general256TiB support. The physical FATX0101/video0093 installation,
0088 rollback and immutable0.1.0 are unchanged. Original111-byte non-ASCII
physical SetupAPI damage remains unexplained and is not attributed to this bug.

Evidence: ../atapi-dump-address/REPORT.md, ../atapi-lba48-network/REPORT.md,
../atapi-lba48-crash/REPORT.md and ../atapi-lba48-recovery/REPORT.md.
All owned runs are closed; no hardware test or further crash is scheduled.
