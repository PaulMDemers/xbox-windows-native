# Dump miniport returns success after addressing the wrong disk region

The final bounded crash004 is CLOSED. Eighteen events and27 resident pins verify
the intended crash, NVNet0104 shutdown completion, dump initialization, first
write and final dump return. All breakpoints were removed and the guest resumed.
The real writer is dump_atapi.sys, matching the pinned owned atapi.sys binary,
RVA13454. It receives the correct64-bit volume offset140436013056, a4096-byte
MDL and the exactPAGEDUMP header/cookie. Its first write returns0; the complete
dump routine returnsTRUE with final status0.

Despite those success returns, three captured ATA command0xC5 register sets
address the lower28-bit region. They request8,64 and56 sectors, totaling65536
bytes. The first decoded LBA is21486704, absolute offset11001192448. The intended
absolute offset is148440145920: exactly137438953472 bytes (2^37) higher. The cold
alias header equals the64 bytes captured from the kernel's source buffer. The
intended pagefile still beginsPAGEPAGE. See wire-verification.json for registers,
binary identity, source bytes, hashes and independently decoded addresses.

Dump qualification is FALSE. No recovery boot was attempted. This narrows the
defect to the dump miniport path below a correct kernel writer call; the precise
instruction/configuration selecting the truncated ATA command remains unresolved.
No speculative patch or settings change was made. The completion screen and
success return are explicitly insufficient evidence of a correct dump.

Cold allocation remains consistent324directories6756files325directoryclusters,
five hives parse and selected protected/payload hashes match. These are bounded
checks, not proof that all contents survive writes to the wrong region. Zero
normal shutdowns is expected for an intentional crash. Physical qualification
and the original111-byte physical corruption cause remain unresolved.

Launch12:48:56UTC; trace finished12:50:17 and owned cleanup followed capture at
12:50:48. Runner96747, tracer15674, supervisor73542, preparation55079 and cold
audit86138 are CLOSED. The initial helper-source newline preflight rejection
occurred before any launch and is retained. Never relaunch/recollect this case.

The NVNet implementation and matched ordinary network/storage PASS were pushed
as693c0cc. Physical0101/video0093, original0088 and immutable0.1.0 remain untouched.
All work here was emulator-only. No actual dump recovery has been qualified.
