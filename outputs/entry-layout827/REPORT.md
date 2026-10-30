# Entry-layout827: read-only kernel sampling

Fresh application samples PCI and current display layout before filesystem calls.
It never selects a display mode, draws, accesses SMBus or enters native code.
Only CRTC selector writes occur, restored and checked. Unknown layouts are raw
observations, not rejected into a presumed mode. PCI mismatch refuses MMIO.
Report is created exclusively on verified E, flushed, closed and read back, then
firmware return requested. Kernel APIs may block; return is not Windows shutdown.

Seven compiled sampler cases passed:720p,640x480,unknown layout,three PCI failures
and failed selector restoration. Host device/service stubs are not hardware proof.
Source/byte/controller review passed. Build001 missing legacy includes and model001
missing MMIO harness mapping are preserved. Build002/model002 are qualified.
The probe checks an unproven826 entry-mode assumption, not the cause of its black
screen. nxdk runtime precedes main, so this is application-entry evidence only.
No hook, no ordinary-launcher changes. Binaries remain private C:/xwn827.
