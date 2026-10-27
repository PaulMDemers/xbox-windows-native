# CR05 low-five-bit checkpoint746

This extends closed kernel744 by the next original SetGPURegister operation,
after the preserving prefix, seven horizontal MMIO words and CR04=93.
Closed native745 independently qualified CR04; no closed runtime is reused.

The retained target nvhtotal779 gives m=747. Original CR05 construction keeps
the freshly read upper three bits and replaces the low five with
(((m+16)/8)-1)&31 = 30. Admitted CR05=0x31 therefore gives target0x3e.
Readback compares the entire byte, including preserved bits, and rechecks
CR04=0x5d. No readback mask, retry, extra CR05 bit7 operation or gate waiver.

Restore this attempt's own saved CR05 first, then CR04, then H7 in reverse
order and the previously qualified prefix recovery. Compare both full CRTC
bytes and all seven horizontal words before re-enabling output. A CRTC or
H7 recovery mismatch leaves output blank and causes immediate durable report
and firmware restart without drawing. Prefix recovery remains independently
checked. Fresh saved values are used; captures are admission evidence only.

The mixed timing interval is deliberately blank. The actual owned900-page
framebuffer remains1280x720x32/pitch5120 and3686400bytes. No vertical, pitch,
scanout, encoder or clock changes. No CR1b/22/33 data writes. This is neither
a complete visible mode switch nor a Windows/native handoff test.

The116-word schema preserves0..111 and adds CR05target/attempted/after and
CR04after at112..115. Existing CR05checked is before the CR05 write.
Forward746d means CR05 full-byte or CR04 interaction failure. Recovery746c
means either final CRTC byte differs from its own saved value. These states
remain distinct from forward success and from the original prefix/H7 faults.

Actual-COFF104 cases retain98 previous cases and add dropped CR05 write,
low/high-bit readback faults, CR04 interaction read/coupling faults, and dropped
CR05 restoration. The independent schema checker and linked PE/XBE checks
validate host contracts only; physical register semantics remain unproven.
