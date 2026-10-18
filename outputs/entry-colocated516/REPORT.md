# Candidate516 built and reviewed; never launched

The new exact510 child moves its320-byte diagnostic data block from95000 to
94c20, wholly within the existing94000 code page. All74 data references move by
-0x3e0. The11100 entry/trampoline,929-byte instruction layout,49 direct branch
targets, imported thunk addresses, original section permissions/image extents,
and retained95000..95140 tail remain unchanged. Five active namespace literals
use XWNBoot516a; the unused old510 literal remains in the retained tail.

Private candidate: `C:/xwn516/build001/default.xbe`,545088bytes,
SHA256 `a272c18d32f96719ddf5ec07dcc551f74165f797b8247b361c1a4e3b3d84da1d`.
The linked raw image is544096bytes; the final XBE explicitly retains the
original tail and original545088-byte length. No image-boundary change is hidden.

Host001 tests the actual Python transformation and inverse checker and rejects
6,503 mutations, including omitted relocations, stale active namespaces, changing
the retained old path, truncated linked-length output, and repaired-digest edits.
It executes no diagnostic instructions, CPU or Xbox API model. Build001 used the
existing build lease and pinned GNU tools. Review001 independently reconstructs
all395 relocations and both linked sections, checks all9 source files against510
after namespace normalization, and joins every changed code operand to its actual
instruction. All other symbols stay fixed;22 data symbols and3 generated end
symbols move. The generated ELF end is not used to shrink the final XBE.
Another399 mutations of actual built bytes were rejected. No test/build failed
in516; the failed515 review harness attempts remain separate and preserved.

One NEW linker warning is retained verbatim: the intermediate wrapper.elf has
an RWX LOAD segment because code and data now share a page. It was not suppressed
or labeled inherited. That ELF is not deployed: the final XBE's original section
flags remain7 and its header is byte-identical except the recomputed section
digest. This warning review is scoped to this diagnostic, not a release policy
or general permission change.

No emulator preparation, physical launch, startup hook or shared source/SDK
change occurred. The physical failure cause remains unknown. Historical494
access and emulator513 translation do not establish current physical mapping;
514 receipt absence still does not prove absence of entry. Its optional LED
report remains pending. Ordinary launcher/startup/720p and Xbox C are untouched.
No boot reliability, Windows/D3D/GPU or release qualification follows from this
build. NEXT.md requires full exact-candidate observer host tests before runtime.
