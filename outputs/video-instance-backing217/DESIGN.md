# 217: inspect the actual dashboard allocator

216 identified the context-switch prerequisite but did not establish instance
backing. This independent diagnostic boots one fresh snapshot child at UnleashX
with the owned Complex4627 BIOS and the exact pinned xemu executable. It never
launches Windows, calls an allocator, writes GPU state or changes the physical
console. This is debugger observation, not ordinary NT5 qualification.

The initial attempts required bounded dashboard FTP readiness; kernel004 and
map005 deliberately remove that prerequisite and inspect the loaded kernel
after a bounded boot delay. Stop the owned CPU, read the PE header
at the expected Xbox kernel base, bound SizeOfImage to 4 MiB, and capture pages.
Explicit RSP unmapped replies are preserved as gaps; corresponding private
container bytes are zero placeholders, never asserted to be resident zeros.
The actual ordinal 168 table entry and a directly reread 1 KiB function window
must be present. The pinned nxdk header and NONAME export declaration identify
the stdcall two-argument ABI; they do not prove allocator semantics.

No breakpoint, register write or memory write is installed. CPU resume and a
completion signal occur during teardown even on failure. The runner has a
180-second bound, snapshot disk writes and owned process cleanup. Source disk
hash is checked before/after. Snapshot clones are discarded by the runner:
there is no cold audit of those discarded children. No NT5 workload or collection is
repeated. Actual BIOS, fixture, launcher, source and resident bytes are pinned.

Inspect exact allocator control flow and globals from the private capture
before drawing a backing conclusion. A stock-kernel allocation is not an NT5
export or an ownership grant through Xromwell. Complex4627 is the emulator BIOS,
not proof of the physical console's kernel behavior. No reset, alias overwrite,
context acquisition or copy experiment follows merely from this inspection.
