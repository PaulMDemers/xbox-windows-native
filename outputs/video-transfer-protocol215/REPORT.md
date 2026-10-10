# Transfer planner and lifetime model215

The CPU-only planner now emits a bounded2D blit packet with a final completion
token, and the lifetime model refuses release until drain. Host002 passed both
O0 and O2 ASan/UBSan runs:18,342,825 checks each,1,024 guarded pixel cases,
100,000 valid/malformed descriptor cases and144 state-transition table cases.
This is host contract evidence. No GPU command was submitted and no speed or
physical qualification follows.

The independent test checks all27 packet words,108-byte length, seven RAMHT
slots/context fields, four DMA descriptors and three graphics descriptors.
Its separate selected-method decoder uses literal method addresses and a pixel
oracle rather than planner-derived expected pixels. Cases vary rectangle width,
height, pitch and offsets, preserve source/guards and alpha bytes, and compare
the complete destination/completion storage. It is a CPU decoder, not real
PGRAPH/QEMU execution. The descriptor oracle accepted12,513 cases, rejected
aliases, overflow, bad alignment/width/pitch/instance spans and zero tokens, and
required rejected calls to leave output unchanged.

The lifetime table covers all eight states against18 events, including pending,
matched/stale/foreign completion, fault, timeout, clock regression, partial
proofs, release and abort. Additional cases check deadline overflow, zero
generation/budget, late completion after quarantine, no context reuse, missing
proof bits and packet-token/header/length coupling. Mock witnesses only drive
these host transitions; they do not prove the corresponding hardware contract.

Host001 also passed its original sanitizer tests, but source review found its
packet and context generations were independently tested. The original source,
result and review gap are preserved under prior-host001 and host001-review.json.
Current preparation now binds the final packet release token/header/length to
the context generation. Host002 separately tests wrong token, absent plan,
wrong terminal header and incomplete packet length. No earlier result was
rewritten and no guest was repeated.

Thirteen private source copies match the actual compiled xemu manifest, including
reconstructed modified sources. Source/evidence review passed49 pins. It proved
the model lacks USER PIO submission and a class39 PGRAPH handler, supports the
62/9f blit path, and orders97 backend semaphore release after surface_update.
It also identified limits: single-slot RAMHT lookup, DMA target/class omission,
27-bit address masking, limit convention, alpha rewriting and context-switch
stalls. All source and binary hashes remain in inventory.json and review.json.

The actual retained214 observations cannot authorize submission. Its681000-byte
Control mapping does not include RAMIN or USER; RAMIN ownership/physical backing,
exclusive context ownership, DMA-address/visibility, global token allocation,
serialization and drain/restoration witnesses are absent. preflight.json records
that hold explicitly. Invented host addresses or proof bits will not be deployed.
See DESIGN.md for the detailed contract and NEXT.md for the next concrete work.

All215 host processes are closed. No new guest/cold scan was necessary for this
CPU-only kit. Closed214 cases were inspected, not relaunched or recollected.
The existing whole-boot Ftdisk49 failure stays distinct from these host passes.
The physical0101/video0093 baseline, original0088 and immutable0.1.0 remain intact.
