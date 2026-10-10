# 218: query-only stock CPU/PRAMIN correlation

217 proves stock CPU allocator arithmetic and a conflicting retained NT5
bootvid layout. It does not prove physical PRAMIN addressing. This independent
NXDK application queriesffffffff without resizing, requires a64MiB kernel
profile/end83ff0000/padding10000, and validates every CPU/MMIO page before reads.
The20KiB reference window is not asserted to be the current claimed-size global.

Read CPU83feb000..83ff0000 and PRAMINfd710000..fd715000 twice using volatile
32-bit loads,20ms between passes, with no display initialization, GPU stores,
cache flush, interrupt acknowledgement, context acquisition or Windows launch.
The reviewed build005 stores four private raw20KiB files plus a report in NEW
E:/xwninst218d using native absolute paths and a NULL object root. Earlier F:
variants are preserved failures; native006 used incompatible large-F geometry.
Directory/file CREATE_NEW guards prevent overwriting prior evidence. Flush files
before an explicit stock-kernel restart request (actual return still requires
observation). This is not a Windows shutdown test.

The pure host comparison checks stability and forward/reversed16-byte block
ordering. Reversal is a hypothesis inspired by older NVIDIA instance addressing,
not an established NV2A fact. Require256 nonzero CPU words and64 unique16-byte
blocks for informative correlation. Equal-zero/repeated content cannot pass.
A stable exact correlation supports an alias hypothesis; no causal write was
made and CPU cache/coherency remains unqualified. A mismatch does not prove that
no physical alias exists. xemu's separate RAMIN is an explicit model limitation.

Build against the existing pinned nxdk58427c0 and runtime, never shared SDK
updates. Review actual imports/disassembly before emulator launch. Use a fresh
owned snapshot/retained child with source/binary/fixture pins and bounded cleanup;
preserve ordinary app observations separately from any debugger observation.
Only a reviewed emulator run precedes authorized physical deployment into a
fresh F: app folder. No boot-menu/startup or Windows driver changes. Keep physical
0101/video0093,0088rollback,immutable0.1.0 and failed evidence.

No result grants NT5 ownership. Afterwards a disjoint layout and explicit handoff
record remain necessary before bounded software context acquisition and16x8 copy.
