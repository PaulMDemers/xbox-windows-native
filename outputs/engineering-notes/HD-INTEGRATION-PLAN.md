# Windows HD integration after the standalone mode tests

Physical connection291 exposes HDTV/component modes on the64MiB Conexant console. Standalone292/297/298 exercise stock Xbox kernel mode APIs. User reported297 looked good; this is distinct from Windows mode programming. Current installed Windows/audio baseline remains unchanged.0.2.0 is deferred.

## Sequence and discriminators

1. Relocation293 moves Cromwell code58->38MiB and stack60->40MiB while preserving4MiB framebuffer and old timing.295 isolated startup passed;296 tests the full Windows handoff, audio/drawing workload, normal restart, and cold integrity against a matched control. Hardware deployment follows this evidence, using a distinct launcher directory and preserving the original launch path.
2. Implement a reservation-only candidate before HD timing. Keep the known low-resolution signal, reserve9MiB at physical55MiB on64MiB machines, and make all consumers agree. Verify actual multiboot map, FreeLdr classification, reserved PFNs, bootvid/provider physical range, stride, hidden backing storage and miniport view. No legacy4MiB descriptor may masquerade as a9MiB allocation. Version and reject incompatible descriptors explicitly. The128MiB case is not implicitly qualified.
3. Capture/review a complete stock-kernel timing reference on this Conexant output: CRTC pitch/overflow/interlace fields, FP timing, clocks/PLL and encoder bytes.292 captured FP timing only. Indexed-register reads must restore selectors; unknown side-effect registers need source/document review first. Native mode success alone does not establish safe Windows handoff.
4. Implement720p first, then1080i with explicit field timing. Preserve visible low-resolution recovery and reject unsupported encoder/cable/memory profiles. Each changes only its reviewed discriminator and gets new pinned emulator/hardware trials. Windows drawable stride must come from actual framebuffer geometry, not analog HVALID alone:640-pixel fallback can have HVALID719.
5. Run repeated full boots, drawing/readback/overlap tests, audio and normal restarts on hardware; verify files/hives/allocation and record TV observations separately. Only then select/tag0.2.0 and assemble its exact private recovery bundle and instructions.

## Memory arithmetic and consumers

1920*1080*4 =8,294,400 bytes. Existing bootvid backing uses640*(480+13+1)=316,160 bytes; total8,610,560 exceeds8MiB.9MiB is9,437,184 bytes and starts at0x03700000 on64MiB hardware. The proposed relocated launcher ends well below40MiB; its heap ends at38MiB. Existing Linux initrd maximum56MiB conflicts with the proposed55MiB framebuffer start and needs an explicit limit/profile decision. Review128MiB multiboot accounting separately.

Consumers include Cromwell memory_layout/clear/scanout/multiboot entries; FreeLdr Xbox memory/video discovery; bootvid reservation/backing and pixel geometry; permanent shared-framebuffer provider descriptor/version/range; miniport mode flags/stride; and the software display driver's RAM shadow budget. A resolution enum alone is insufficient. Native GPU ownership/acceleration remains a separate deferred project.

Strict inherited failures (Windows Ftdisk49 and standalone reserved-sector disk inequality) remain visible; none becomes a PASS because an HD pattern looks correct. No release tag, original rollback, or previous evidence is rewritten.
