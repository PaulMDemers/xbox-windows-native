# CR04 checkpoint744

This adds one register access to closed kernel742's qualified preserving prefix
and seven horizontal MMIO writes. Native743 separately passed that prefix;
no closed runtime is reused. No installed launcher or Windows driver changes.

The retained SetGPURegister sequence next computes m=nvhtotal-32 and writes
CR04=m/8. Its explicit target nvhtotal779 yields93 (0x5d), with integer division.
The initial CR04=a7 and CR05=31 are admission guards from743's retained kernel
pre-arm capture. Recovery uses this attempt's own freshly saved byte, never a
borrowed snapshot. Full-byte readback behavior is the hardware question, not
an assumption established by the host model.

Admission retains CR11 bit7 clear, the same indexed CRTC/SEQ/GR ownership and
the complete742 setup/H7 baseline. Output is blanked using the qualified SEQ1
and gate sequence. After all15 prefix and7 horizontal comparisons pass, write
CR04 once and read CR04 plus adjacent CR05. CR05 is never written. Full byte93
and unchanged CR05 are required. There is no masking or retry of a mismatch.

Restore CR04 first, read it and CR05, then restore H7 in reverse order and
check all7. Recover the existing prefix CR19/680630 afterward. Do not re-enable
output if either the CR04/CR05 or H7 recovery check fails. Save the112-word
result and request firmware restart immediately, without drawing or waiting,
in that case. No guessed restoration of CR05 is allowed. Other prefix cleanup
checks remain unchanged and are independently reported. A requested restart
does not establish return; authenticated dashboard and collected records do.

CR04 affects horizontal sync start, not the framebuffer address, pitch or
vertical extent. The temporary mixed horizontal state is intentionally blank.
The inherited conservative fetch bound (5120*720=3686400) remains within the
owned, physically checked900-page1280x720x32 framebuffer. This is not a visible
480p switch. Do not continue to CR05, vertical timing, encoder, clock, scanout,
CR1b/22/33 data writes, full replay or Windows from this result alone.

Actual-COFF tests cover all inherited89 cases and9 new cases: two baseline
refusals, CR04 bad read/dropped write/bad recovery read/dropped restoration,
CR05 transient forward/recovery read mismatch, and persistent modeled coupling.
Every restoration fault is required to inhibit output-enable. The full trace
requires CR04 restoration before H7 reversal; no CR05 data write is admitted.
Linked code and data are checked in the PE and XBE. The model verifies control
flow and access contracts, not electrical timing or physical GPU semantics.
See FAILURES.md for the preserved source-generation and harness failures.
