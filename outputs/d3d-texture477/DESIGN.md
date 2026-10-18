# Rung08a owned texture control

Use a fresh PC child of the reusable 404 clean NTFS installation. Two isolated
NT5 processes select the actually enumerated RGB software device through default
and explicit HEL DirectDraw creation. No primary surface or display change.

Enumerate at most 64 actual texture formats. Select the first exact 32-bit RGB
or ARGB format with 8-bit RGB masks; retain the complete enumeration. Unsupported
formats refuse. Upload an owned 8x8 system-memory texture: R=32+24x, G=32+24y,
B=32/224 by checkerboard parity. This identifies every texel and both axes.
Alpha is 255 only for the enumerated alpha format, otherwise the unused byte is
written zero. Capture all 256 source bytes before draw and after draw unchanged.

Render two XYZRHW/UV triangles spanning (8,8)..(56,56) into a separate 64x64
RGB32 system-memory target. Explicit point min/mag filtering, no mipmapping,
clamp U/V, texture stage SELECTARG1/TEXTURE, no texture transform, alpha/depth/
lighting/fog/dither/antialias disabled. Texture source and target are distinct.

Independent Python oracle is fixed before launch: 4096 clear RGB pixels; 3x3
safe interior samples in each six-pixel texel cell (576 exact RGB samples),
exterior background, and only source-palette/background values at unqualified
edges. Exact raster/sampling-edge selection and unused target X bytes are not
qualified. Point-sampling boundary caution is consistent with Microsoft's
[nearest-point documentation](https://learn.microsoft.com/en-us/windows/win32/direct3d9/nearest-point-sampling);
this is supporting sampling background, not a claim that D3D9 is the tested API.
Actual API declarations/macros come from pinned D3D7 RosBE headers.

Require API results, balanced releases, module snapshot/PE hash closure, process
exit receipts, normal guest restart, cold file/hive/event checks and independent
NTFS reader. Synthetic tests are not runtime evidence. No driver change, GPU
acceleration, presentation, depth/blending, performance or game compatibility
claim. Only a qualified PC result supports a distinct physical test.
