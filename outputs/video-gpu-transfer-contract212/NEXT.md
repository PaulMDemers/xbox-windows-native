# Next transfer step

Read213's closed results first; never rerun212 host kits or closed213 children.
Keep individual source/binary hashes authoritative. pbkit is a pinned reference;
the NT5 build/toolchain and permanent UC framebuffer contract stay unchanged.

Before a first GPU transfer, establish instance/context ownership and a supported
resident command/source/destination address and lifetime contract. Inventory
firmware and current miniport GPU state through a bounded read-only diagnostic;
do not initialize/reset globally from a pbkit recipe. xemu's separate RAMIN model
must remain an explicit physical qualification gap. The conditional20KiB overlap
is a reason to investigate, not a chosen allocation or proved collision.

Then implement one serialized context with resident sequence/completion and
bounded drain/quarantine behavior, initially using disjoint guarded16x8 storage
and an independent CPU oracle. No scanout writes, modes, cache conversion or
physical deployment until those contracts are concrete and reviewed. A successful
allocation precursor does not establish GPU addressing, completion or crash safety.
