# 547 native-format presentation bridge

546 is closed: the PC Cirrus driver refused RGB32 mode before either sample
ran. Its private frozen inputs and failed mode receipt are retained. Use a
fresh child of the original 404 seed; do not parent or rerun 546.

Keep the RGB32 offscreen D3D scene unchanged. Copy its RGB values into an owned
system-memory presentation surface matching the existing primary's RGB32,
RGB565 or RGB555 format. Quantization is explicitly high-bit truncation;
capture the exact packed native pixels before and after the primary blit.
The GDI screen capture uses that same native bit depth and masks, avoiding an
ambiguous 16-to-32 color expansion. Store native samples as zero-extended
DWORDs, with unused RGB32 X or RGB555 top bit outside the claim. Require exact
native presentation pixels, clipping, occlusion, guard colors and source
preservation. This CPU conversion step is part of the tested path, not GPU
acceleration or a direct RGB32-target blit claim.

No mode changes on PC or Xbox. Retain the five independent RGB32 scene cases,
original geometry oracle and its edge bands. New host controls independently
derive packed native values from those validated scene pixels and check every
GDI pixel exactly. Test all three formats with synthetic controls before a new
PC launch. Require actual PC completion before any new Xbox package is staged.
