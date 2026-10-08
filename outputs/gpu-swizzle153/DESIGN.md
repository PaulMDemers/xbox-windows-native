# Swizzled drawing and CPU writes

Actual triangle draws exercise A8R8G8B8/Z16 swizzled surfaces in64×32 and32×64
shapes. NV2A clears use a linear path, so this kit avoids clears entirely. CPU
initialization fills two32,768-byte arenas with0xa5; vertex/fragment passthrough
shaders draw a magenta rectangle and write Z16 zero with depth ALWAYS. Read both
arenas, patch two pixels in each through rectangular Morton addresses, read again,
then draw an overlapping cyan rectangle and read both arenas a third time.

The independent Python oracle constructs address-bit positions from dimension
lengths; the guest emits an iterative bit-deposition loop. Known small coordinates,
rectangular tail bits and full2048-pixel bijections validate the oracle before
launch. Entire arenas include all bytes beyond the active surface. Require twelve
exact snapshots, eight CPU stores, normal reboot/dashboard, unchanged E files and
chains, full allocation ownership and no top-overlay F writes. Sparse traces must
prove actual swizzled create/upload/download geometry and candidate CPU eviction.

Reuse build003 matched xemu executables. Compile only the private nxdk diagnostic
app, using unchanged shared SDK and pinned shader compilers. Use new unique fixture
and run IDs; retain failures. FTP observation uses the whole-exchange deadline
helper from152. No Windows, physical or performance qualification is claimed.
