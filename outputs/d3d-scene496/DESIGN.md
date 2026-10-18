# Combined XYZ/texture/depth scene496

The frozen495 oracle is copied byte-exact to tools/graphics_scene_oracle.py.
Actual scene.c submits six XYZ|TEX1 vertices, two owned 8x8 textures, a queried
attached depth surface and five explicit matrix/order/depth controls. Captures
are offscreen RGB; all setters/readbacks, inventories and release results must
pass the strict independent metadata decoder before pixel checks qualify.

Host tests use synthetic metadata/COM objects and allowed-color frames. They
verify rejection and transport, not actual guest or device execution. Frozen495
literal geometry/pixel witnesses and negative controls remain separate evidence.
No pixel expectation changes after a guest launch. No visible presentation,
varying-W interpolation, GPU acceleration or performance claim.

Plan: host transport negatives, leased RosBE compile/import review, fresh unused
404-seed PC child and bounded90/600second runner, independent cold/module audit.
Only that completed PC control permits a distinct matched Xbox candidate.

Host001 failed a synthetic source-capability negative: 0x41800 does not set the
DDSCAPS_MIPMAP bit (0x400000). Host002 corrects that test to 0x401800; actual
sample, decoder and frozen oracle are unchanged. Both private inputs/results
are retained. Five host002 groups pass, including every metadata field removal
and corruption. Build001 and 24 runner/26 sample NT5 imports pass.
