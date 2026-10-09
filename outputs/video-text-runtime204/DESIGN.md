# NT5 text upload validation, 204

This new kit tests the exact 203 matched builds, with XWN_TEXT_BOUNDS OFF/ON;
phase clocks and scalar UC stores are OFF in both. It keeps the exact joined202
runner, bounded201 known-wizard helper, actual setup-idle gate, five within-boot
samples, byte-exact SetupAPI bookends and unforced restart guard. Persistent device
policy remains the captured physical core, without synthetic null bindings.

The version10 probe retains the199 copy, DIB, timing and40-window-move checks. It
adds13 cases: transparent and opaque text, extended and empty ETO_OPAQUE rectangles,
actual italic/underline/strikeout metrics, rotated font, negative and bottom-right
origins, simple and disjoint complex clipping, and Unicode glyphs. Each compares
all32768 pixels with a separate DIB rendered by the same native GDI API, including
unchanged guard pixels. Each also asks the driver to compare the entire RAM primary
with actual scanout. The latter catches an under-upload that RAM readback alone
would miss. This is not an independent glyph rasterizer test.

Immediate117 escape packets surround only the target screen text call and GdiFlush.
No logging occurs between them. A call-count delta other than one fails isolation,
apart from the empty opaque case where GDI may use BitBlt and produce zero text
calls. New counters record actual row-copy bytes; the probe independently counts
the intersection of returned bounds, client pixels and the selected clip. Whole
client upload is expected in OFF mode. Geometry and bytes are checked without
subtracting unrelated device-global counters. No unexpected extra or invalid
metadata runtime coverage is assumed from host tests.

An owned black popup covers the desktop behind the measured window. Its paint
handler never draws text. It reduces background exposure work while retaining the
visibility checks and both GDI rendering paths. It does not cancel dialogs, disable
devices, change services, or establish a globally idle graphics system. Unknown
pending installation still prevents the runner from measuring.

Before and after each fresh standalone sibling: full allocation, five structural
hives, protected file hashes, typed service/device/dump policy, event and SetupAPI
history, measured interval, normal shutdown and dashboard return. Whole-boot
warnings remain strict failures. Known Ftdisk49 is not silently waived. No emulator
timing is physical performance evidence. Physical testing needs a new readback
verified capture/proposal/rollback and exact payload/helper/probe pins.

Initial preparation failed at importing libhivex, before an attempt directory,
disk write or launch. The retry supplies the owned LD_LIBRARY_PATH. That host
failure is retained in prepare-import-failure.json. Copied old protocol docstrings
refer to202/profile clocks; this document and actual203 build definitions define
the new bounds experiment. Actual driver hashes in fixture records override the
old198 payloads; the miniport and boot-video remain identical.
