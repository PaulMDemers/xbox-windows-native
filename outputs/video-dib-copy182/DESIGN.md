# Bounded DIB upload114

The measured upload pays both the GDI engine and RAM-to-UC upload costs. This
candidate replaces only an eligible standard32bpp SRCCOPY into the owned RAM
primary with exact row memcpy. The existing scanout upload remains unchanged.
It changes no cache attributes, modes, GPU use, surface ownership or lifetime.

Eligibility requires a standard system-memory32bpp source, the registered
primary destination, absent translation or exactly XO_TRIVIAL, and absent,
trivial or rectangular clip. BitBlt additionally requires ROP4 0xcccc and no
mask. Complex clips, other formats/ROP/translation, readback and primary overlap
retain the current engine path. Entire advertised surfaces and requested source
and target rectangles must fit their allocations before any write. Signed row
strides are supported. Allocation alias, overflow, unknown geometry and
unsupported cases fall back. Empty rectangular intersection is a successful
no-op. Every accepted row copies all four bytes per pixel; scanout checks compare
RGB under the established unused-high-byte contract.

A separate read-only128byte escape0x58574434/version114 reports enabled state,
attempts and result counts plus bytes. Existing112 escapes remain ABI112 for
the unchanged geometry/scanout probe. Existing membership semaphore protects
only new accounting/snapshots, never rendering/memcpy. Counters saturate rather
than wrap. Both control and candidate include this accounting; the build flag
alone enables copying. Timing compares matched builds, not untouched112.

Host geometry/redzone oracle and matched fresh compiler/import/residency review
precede any fresh ordinary emulator pair. Runtime must show positive eligible
coverage, exact pixels for both source orientations/clips and fallback cases,
normal guarded restart and full cold integrity. Inherited Ftdisk49 stays a
strict failure. Emulator timing is not physical-console performance. Preserve
the settled181 emulator null-device policy explicitly; no physical access.

DDI contracts consulted: Microsoft [DrvCopyBits](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvcopybits),
[SURFOBJ](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-surfobj),
and [XLATEOBJ](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-xlateobj).
Private format translations and non-system-memory bitmaps are not assumed safe.
