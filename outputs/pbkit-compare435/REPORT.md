# 435: same framebuffer comparison completed; visual result pending

One accepted physical launch at 2026-10-17 05:29:52 UTC completed all four
observations and requested firmware restart. Dashboard collection closed at
05:31:29 UTC. Native terminal error0, PBKit init return0, four complete phases.
The application journal spans about44 seconds. All owned host commands closed;
no second launch queued. Never rerun/recollect this consumed case.

Two orange-bar 1080i phases precede normal PBKit initialization. Two cyan-bar
phases follow it and the supported `pb_show_debug_screen` call. Both pairs
show original and one-row-shifted parity. Each phase has 524,288 independently
verified pixels: 2,097,152 total, 8,388,608 bytes. The full native framebuffer
also passed its same-helper check; that is not an independent full-frame oracle.
104 mutations of actual headers/pixels and203 synthetic transport mutations
were rejected. No camera/HDMI capture is included.

All four phases use the same stock framebuffer physical0x037f7000, allocation
8,294,400 bytes, pitch7680, 1920x1080x32 mode. Recorded available pages before
init14186 (58,105,856 bytes), exceeding the unchanged48MiB preflight. PBKit
returned0 in224ms of journal ticks. Its transient normal frontbuffer switch is
recorded in the journal; the observed cyan phases return to the original buffer.
No PBKit tiled buffer was CPU-written and no application GPU draw submitted.

Among the23 CRTC and29 MMIO registers captured, only PCRTC_CONFIG0x600804 changes:
3 before,2 afterward. CRTC pitch and output height remain correct. This is a
limited register inventory, NOT proof of a one-register change: PBKit also
initializes interrupts, DMA, tiles, gamma and other state, including CRTC31/82
outside this capture. We cannot identify a cause or fix from CPU pixels alone.
The user was asked whether cyan restores stripes or retains orange's parity loss;
that visual answer is pending. 1080i remains unqualified and720p remains default.

Build001 XBE SHA256
`edbbc2efcbf4ecf9912d26fc5b1c916a77cb70cc949347fbba3bade38960b715`,143360 bytes.
Shared SDK/library/header/tool hashes unchanged; installed nxdk prebuilt libs,
not a full SDK rebuild. Only inherited edata merge warning. Source/binary/host
closure in review004.json. Six runtime files double-read and rehashed privately
under C:/xwn435/physical001. No Windows startup/driver/launcher change, Xbox C
access or system image deployment. Protected physical baseline and720p selector
unchanged. This standalone restart is not Windows shutdown or disk-wide audit.

Failures/corrections retained: review001 byte comparison rejected the copied
pattern's newline difference; its diagnosis reversed the direction. review002
retains that reversed-direction failure. Actual435 source is CRLF514 bytes and
430/434 source LF499 bytes; normalized bytes exact. review003 expected an
undecorated callback symbol but the actual stdcall map has `@4`. All three prior
review sources/failures remain, and the native build was never altered/rebuilt.
review004 qualifies the unchanged build. Frozen DESIGN.md allocation sum is
16384 bytes too high; source-review.json records the correct44,236,800-byte
PBKit color/depth total. Actual48MiB preflight remains conservative and unchanged.

SDK init/file/shutdown functions contain synchronous paths without independent
cancellation. Native terminal plus dashboard return support completed lifecycle,
not exhaustive cleanup instrumentation. Two initial dashboard polls timed out,
then the next connected; no launch retry/reset was sent.
