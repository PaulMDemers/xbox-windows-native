# 681 Xcalibur480p source review and host prototype

**Host-only. No Xromwell XBE, Windows package or maintained driver was changed.**
The incoming1.6 still needs a watched baseline and native qualification.

## Findings

The maintained explicit480p/720p transaction accepts Conexant only. Its explicit
480p wrapper fails closed on an unsupported encoder; the default720p wrapper can
fall back into legacy initialization. That fallback is not a reviewed1.6 profile.

The legacy Xcalibur HDTV routine always allocates/copies the480p table, ignoring
the requested HDTV mode. Its encoder writes ignore errors and use unbounded
SMBus waits. The shared four-byte read consumes four FIFO bytes without storing
them in the caller's output. These are source findings; they do not establish
why any particular physical boot failed. The fallback encoder detector labels
Xcalibur after failed Conexant/Focus probes; retain `unidentified` instead until
there is independent evidence.

Primary source: [Cromwell Xcalibur driver](https://github.com/XboxDev/cromwell/blob/master/drivers/video/xcalibur.c),
[SMBus helper](https://github.com/XboxDev/cromwell/blob/master/drivers/pci/i2cio.c).
Local immutable inputs and their SHA256s are in `sources.json`; the tested parent
is the strictly reconstructed677 source tree, not today's moving upstream.
The copied common GPU source retains Oliver Schwartz's GPL notice. The encoder
table retains Cromwell provenance; experimental derivatives are GPL-2.0-or-later.

## Implemented and tested

- `xcal_bus.c/.h`: callback-based four-byte SMBus transactions, correct read
  assembly, exact block-length checking, bounded poll count, combined
  completion/error rejection, no retries, and unchanged caller output on failure.
  Busy/dirty entry returns before any writes. Only terminal status observed from
  this transaction is acknowledged; no pending-status repair or controller reset.
- `xcal_profile.c/.h`: separately gated480p encoder-table sequence. It requires
  independent Xcalibur confirmation, HDTV/480p configuration and the exact
 64MiB/55MiB/9MiB/316160-byte reservation contract. It preserves legacy reset,
  register order, byte order and500µs delay requests, and stops on the first
  failed transaction or delay. No allocation, GPU writes or Windows admission.
- `host001.json`: GCC12 ASan/UBSan passed66,164 protocol/profile cases plus full
 720×480 pattern bounds. Includes all16-bit entry statuses,64 low status values,
 256 returned lengths, failure at each of148 transactions and144 pauses,
  incompatible request rejection, exact table byte order and sequence.
- `gpu001.json`: four fresh isolated executions of the retained compiled
  `SetGPURegister` function, with different initial CRTC bytes. The source's
  Xcalibur480p inputs produce720×480, pitch2880 and format3 (32-bit). Totals are
 779/524. The resulting visible extent fits the reserved window. The routine
  does not write the framebuffer start or pixel clock in these fixtures.

The Windows miniport consumes PRAMDAC dimensions, CRTC stride/format and PCRTC
framebuffer start. This geometry fits its existing expectations; no justified
pixel-format or allocation patch is established yet. The legacy GPU-to-encoder
YUV conversion registers do not by themselves mean the Windows framebuffer is
YUV. Physical color bars must verify the end-to-end result.

## Boundaries and next step

The bus model supplies completion/error semantics; it does not prove MCPX block
protocol behavior, register writability or Xcalibur output. Poll counts are not
elapsed-time deadlines. There is **no native I/O/timer binding** yet: it must
account for actual initial controller status without clearing an unknown pending
transaction, preserve port width/ordering, and independently bound the requested
delays. Earlier whole-firmware startup also has unbounded helpers outside this
prototype. The four-byte response is not a silicon-ID register.

The actual compiled GPU routine is tested in isolation, not a boot. No stock
xemu execution is treated as an Xcalibur hardware model. Clocks, output conversion,
scan timing, framebuffer reservation/handoff and visible pixels remain physical
qualification work. First use680's kernel baseline; then build a separate native
480p pattern-only candidate before Windows. [NEXT.md](NEXT.md) gives the gates.
