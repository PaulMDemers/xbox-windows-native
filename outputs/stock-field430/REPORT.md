# Stock Xbox comparison reproduces the reported mode difference

physical003 completed both stock-kernel modes and all eight capture phases, then
returned to UnleashX. The independent oracle verified4,194,304 pattern pixels;
every volatile framebuffer readback comparison passed. Actual mapped framebuffer
physical addresses equal the hardware scanout address in both modes, with valid
allocations and unchanged per-mode state. The user reported:

> on 720 everything looks perfect, on 1080, every other column is a solid color.

This is visual evidence of a mode-dependent difference without Windows or
Xromwell running. It supports investigating the shared interlaced output path,
not a speculative Windows font/BitBlt fix. It does not identify the adapter, TV
deinterlacer, Xbox encoder or exact lost rows. Some vertical binary-label bands
are intentionally solid; photographs and band-specific interpretation remain
necessary. No new photographs were attached. The user did not separately report
the two-line versus one-line or stationary versus moving outcomes.

Stock runtime readings for14 RAMDAC timing registers in each mode equal the
corresponding public launcher profile constants exactly. This is not a live
Windows register comparison, full CRTC/encoder dump or signal capture. The stock
SDK calls the kernel AvSetDisplayMode and uses its normal filters; our code makes
no custom register writes. Moving paint is single-buffered and unsynchronized,
so ordinary tearing remains possible. No Windows text is rendered by this tool.

The launch was accepted at2026-10-17T03:05:24.536UTC from the new owned path
E:/Applications/XWNField430c/default.xbe. All four phases at each resolution ran
about10 seconds. Moving phases completed170 frames at720p and132 at1080i; these
are diagnostic coverage counts, not a Windows performance comparison. Eight
captures, result.bin and the exact XBE were retrieved twice and rehashed under
C:/xwn430/physical003. The initial/terminal records and all phases pass. The
source requests HalRebootRoutine after closing results; dashboard return was
observed. No claim of a Windows shutdown or whole-disk allocation audit.

Protected Windows files, original startup and the exact720p launcher remain
unchanged. No dashboard C access, driver replacement, EEPROM change, menu edit
or Windows startup hook. No physical test is queued; all host sessions closed.
The standalone helper is one-shot and its files are retained as evidence.

Build003 XBE SHA256:
f10bf211e0035d60a625227be662921fa8c5269074e376a06d9eba2b449a020b.
Shared nxdk sources/libraries/tools were pinned before/after each build and
unchanged. All builds used existing libraries under the cooperative build lease;
no SDK rebuild. The one inherited export-section merge warning was reviewed.
Host001 tests actual paint with ASan/UBSan and independently checks23,961,632
pixels/guards; video flush is modeled. The record decoder rejects64 modeled
mutations. analysis002 additionally rejects96 actual-record mutations and checks
all private captures/addresses/timing subset. No emulator run was performed.

Preserved failures: build001 referenced unavailable WinAPI FlushFileBuffers and
failed compilation. Build002 used E: DOS paths; physical001 returned no result.
The linked nxdk startup only guarantees D: at the XBE directory, so missing E:
is the source-supported explanation, not an observed failing NTSTATUS. Build003
changes only those paths/comment. physical002 refused before any mutation due
to a stale lowercase directory guard; physical003 derives that guard from REMOTE.
analysis001 incorrectly assumed HDTV enum1; the pinned SDK defines4. Its failed
checker remains separate from corrected002. No failed attempt was rerun or
retrospectively qualified.
