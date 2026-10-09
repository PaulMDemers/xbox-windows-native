# Scalar UC row-store115 comparison

183 proved bounded direct DIB copies but showed no upload benefit. The compiled
old row copy already uses aligned REP MOVSD. This original115 experiment starts
from112, keeps every GDI engine path and complex-clip enumeration unchanged, and
compares the existing row memmove with an eight-word unrolled scalar sequence.

Both sequences copy precisely the same row bytes, forward. Candidate requires
aligned source/target, nonzero word-sized length, no address wrap and disjoint
virtual row spans; otherwise it uses original memmove. Caller remains the existing
qualified owned RAM/scanout pair and bounded rectangle. These checks choose a
copy implementation, not a new external-pointer API. Scalar destination stores
are volatile32bit full expressions, with alias-safe builtin four-byte source
loads. No FPU/SIMD instructions, wider write, cache attribute, mode, GPU, surface
ownership/allocation or lifetime change. Actual compiler output must prove these
instruction properties before launch.

New read-only escape0x58574435/version115 counts upload boxes/fast and slow rows,
total bytes and fast bytes. Accounting/snapshot only under the existing membership
semaphore, never across copying/rendering. Both matched builds include accounting
and differ only XWN_UC_STORES OFF/ON. Existing112 ABI/scanout comparison stays112.

Host redzone/alias/tail/alignment/wrap byte oracle precedes matched ordinary
emulator boots on preserved settled181. Exact pixels and actual fast-row coverage,
normal restart/full cold audit and unchanged strict events are required. Emulator
REP/scalar timing can differ from physical CPU/bus timing; a useful emulator
result is only a hardware benchmark candidate, not a physical speed claim.
Keep inherited null-device policy explicit and Ft49 strict failure. Preserve all
earlier failures, physical0101/video0093/0088rollback/immutable0.1.0. No physical
access in this experiment.
