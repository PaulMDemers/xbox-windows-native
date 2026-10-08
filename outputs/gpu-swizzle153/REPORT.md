# Swizzled drawing: both original depth oracles fail

Both153 cases return normally and pass protocol, exact file set and full cold disk
safety checks. Six color snapshots per case match. All six Z16 snapshots fail the
frozen oracle: drawn depth is1 where it expected0. Both cold_passed values remain
false. The forensic W-buffer reference in verification.json does not waive them.

Each case draws on64x32 and32x64 swizzled A8R8G8B8/Z16 targets. CPU initialization,
two sparse pixel changes per arena/shape and a second overlapping draw exercise
GPU-to-CPU and CPU-to-GPU coherence. Each32768-byte snapshot checks active pixels,
unused arena tail and padding. Rectangular Morton addressing is independently
checked as a bijection;67 oracle tests pass. Ten negative lifecycle tests reject
missing downloads and wrong layout, pitch, pixel size or eviction reason.

The pinned shared pbkit source selects W-buffering when binding the target:
NV20_TCL_PRIMITIVE_3D_W_YUV_FPZ_FLAGS is0x00110001. All probe vertices have w=1.
Pinned xemu shader-generation source selects vtxPos.w for this state, explaining
the identical depth1 in both builds. This is a probe state mismatch; no emulator
patch is made.153 remains unchanged, with original Z=0 oracle failure preserved.

The compact traces show both shapes as swizzled, the requested pitches/pixel
sizes and actual uploads/downloads. Candidate has three CPU-write evictions per
arena, including next-shape CPU initialization; control uses incompatible-layout
replacement. E allocation, existing E contents/chains and entire F are clean and
unchanged. No Windows, hardware or performance validation.154 is a fresh compiled
probe explicitly selecting Z-buffering and two distinct depth values.
