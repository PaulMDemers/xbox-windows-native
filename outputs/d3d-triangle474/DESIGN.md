# Rung07: RGB software triangle

This new sample enumerates the installed D3D7 devices and requires exactly one
RGB software GUID, clear hardware-rasterization/TnL flags and declared 32-bit
render support. It creates its own 64x64 RGB32 SYSTEMMEMORY, OFFSCREENPLAIN,
3DDEVICE surface. No primary surface or display mode is changed.

The target is cleared to RGB 10/20/30 hex. Three pretransformed XYZRHW/diffuse
vertices at (8,8), (56,8), (8,56), z=0.5 and rhw=1 use RGB 40/c0/80 hex.
Depth, lighting, culling, fog, blending, alpha test, dither, specular and
antialias are explicitly disabled. Solid/flat and diffuse selection are explicit.
There is no texture, z-buffer, presentation or hardware-acceleration claim.

Two complete 16,384-byte captures retain the original XRGB bytes. The independent
checker requires every clear RGB pixel, 561 triangle interior pixels and the
predefined exterior region. The boundary band must contain only background or
triangle RGB; its exact coverage is not qualified. The unused fourth byte is
retained but not compared. The oracle is fixed before runtime.

Each lock checks format, dimensions, positive bounded pitch and surface caps;
copies only 256 owned bytes per row; unlocks before release. Live modules are
enumerated while the device exists, bounded to 64, then independently matched
to cold files. A snapshot is not a history of every previously unloaded module.

The external controller runs default and HEL requests in separate processes with
90-second deadlines and exclusive result names, then requests normal restart.
An API failure remains a failed result; successful file capture alone does not
qualify pixels. Fresh404 NTFS child first, distinct physical case only afterward.
