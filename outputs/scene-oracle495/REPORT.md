# 495 combined-scene oracle: host-only PASS

Five host test groups pass for a proposed two-triangle XYZ/texture/depth scene.
The ordinary two draw orders agree when depth is enabled; depth-disabled,
zero-depth-clear and world-motion controls produce distinguishable outputs.
Independent literal projection/color witnesses supplement the synthetic images.

Host003 rejects61,440 invalid RGB words across every frame/pixel,2,048 exact
source-byte mutations,22 plausible wrong scenes (including missing primitives,
constant textures and swapped layers), and18 invalid extents/types. High color
bytes are explicitly excluded from RGB checks. Safe-region counts in the first
two frames are near346/far54/background2536; movement has335/69/2546.
The fixed two-pixel bands and minimum20/20/2000 coverage gates are unchanged.
See coverage003.json for every frame and exact rational projected coordinate.

Host001 failed before any runtime because only15safe far pixels remained.
The source/test snapshots and failure are immutable in C:/xwn495/host001.
Host002 strengthens geometry and prevalidates all masks before running negative
cases. Host003 adds eight independent literal pixel witnesses and10 missing/
flat-texture negatives. Its oracle is byte-identical to002. All six private
source/test files rehashed; final-review.json records exact provenance.

No Windows sample has been compiled or executed for this scene. No actual
metadata/transport decoder, textures, renderer behavior, guest/hardware pixels,
windowed presentation or lifetime result is established. All five host groups
use synthetic images. Constant W/depth pertriangle means varying-W perspective
interpolation is also unqualified. No console access, SDK/driver change or
owned long-running process occurred. 494 remains the latest physical result:
scopedXYZPASS/strictFALSE withFtdisk49/shutdownpopups preserved.

Next496 implements the actual sample and independent metadata/transport checks,
then a fresh PC control. Only successful actual coverage supports a subsequent
matched Xbox run. No expected pixels may be fitted to runtime output.
