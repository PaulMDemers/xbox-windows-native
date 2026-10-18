# Static extent review519 passed; no runtime or saved candidate

The exact516 linked image ends at94d60. Its deployed XBE retains another992bytes:
672zero padding bytes and320bytes of old data at95000. An in-memory proposal
removes that tail, changes the three image/section length DWORDs and recomputes
the section digest. Remaining live/payload bytes, entry, permissions, imported
ordinals, TLS bytes, namespace and all code/data addresses are identical.
The proposed file is544096bytes, with rounded image end95000 instead of96000.
No proposed XBE was saved, built or executed.

Independent inspection reconstructed all395 object relocations and both linked
sections, joined the actual raw wrapper with final header/payload, and verified
74data references,49direct edges,8indirect edges and nine bounded data buffers.
There are no absolute relocation targets in the removed tail. Actual disassembly
is byte-identical to pinned516's retained disassembly; the current objdump hash
matches the pinned build tool. Known entry-only code/data references fit below
94d60. External kernel behavior, caller stack and inherited TLS runtime handling
remain separate unknowns; this is not a proof over arbitrary external execution.

The independent inverse validator rejected5488 actual byte mutations, including
mutations with repaired section digest, and six invalid lengths. Historical494
and518 physical cold files were rehashed and joined to their staged/built images.
494's rounded end is95000, but this correlation does not establish that an extra
page causes518's absent receipt. The generic TLS sanity check still fails on
the same unchanged bytes in successful494 and in516/proposal; no TLS fix was made.

39inputs and two small private review files rehash exactly. Review93375 and final
review closed successfully; no compiler, emulator, console connection, hook,
new launch or shared source/SDK modification occurred. No test failure occurred.
The original516 file and518 failure remain unchanged. No ordinary stability,
Windows, D3D, GPU or release qualification is claimed.
