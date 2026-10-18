# Data-layout review515: static proposal passes, physical cause unresolved

The exact510 entry diagnostic reads `entry503_state` at `0x950f0` before its
first LED call. Its 320-byte data section occupies `0x95000..0x95140`; the code
ends at `0x94c18`. The intervening 1,000 bytes are zero in the retained image.
An aligned copy at `0x94c20..0x94d60` fits wholly on the existing `0x94000` code
page. This provides a distinct, narrowly bounded layout experiment to prepare.
It does not establish why physical514 produced no receipt.

Review004 reconstructed both complete linked sections from the retained ELF
object and all395 relocations, byte for byte. All74 references to the data section
are accounted for:72 in the diagnostic code and2 internal data pointers. An
independent byte scan finds exactly those72 code pointers; independent objdump
decoding confirms their instruction boundaries and adjusted operands. All49
direct control-flow targets remain unchanged. Imported thunk addresses and the
failure adapter's code target remain unchanged; only the pointer slot moves.

The proposed image existed only in host memory with the old510 namespace. It is
not an assembled candidate and was neither saved as an XBE nor launched. Its
entry/trampoline, imports, section/image extents, untouched gap, and old data tail
are preserved. The section digest is recomputed. An independent inverse
normalization checker rejects5,822 image/pointer mutations and10 invalid bases,
including every omitted relocation with an otherwise repaired section digest.
Only the929-byte diagnostic fragment and textual inventories were saved privately.

Historical494 context bytes were rehashed and decoded offline, joined to its
actual ELF symbols: the packet at `0x94558` and capture code
`0x9473e..0x94877` lie on `0x94000`. That establishes historical accesses on this
page, not the current mapping or access to the exact proposed addresses.
Emulator513 has actual successful `0x95000` translation/API evidence; physical514
has no corresponding mapping observation. Absence of its receipt does not prove
absence of entry. The user's514 LED/screen observation is still pending.

Failed reviews are retained unchanged:001 passed section reconstruction but
failed the Windows-to-WSL path conversion;002 reached raw-fragment disassembly
but used `-d` where `-D` was needed;003 completed the layout controls but tried a
mistakenly renumbered historical JSON path.004 corrects these harness references.
The ELF reader/layout contract and retained510 inputs did not change between
executed reviews. No closed physical/emulator attempt was rerun or recollected.

No candidate build, guest preparation, physical access, startup hook, shared SDK
or driver change occurred. Ordinary launcher,720p and Xbox C remain untouched.
Matched486 alpha and496 scene evidence remain pending; this adds no D3D, GPU,
game, boot-reliability or release qualification. See final-review.json for final
input/private hashes, process state and capacity; NEXT.md defines the next gate.
