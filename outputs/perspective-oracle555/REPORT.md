# 555 host perspective oracle

Five exact-rational cases: equal W, increasing W, decreasing W, swapped UV,
and uniformly doubled W. Two disjoint triangles retain identical projected
outlines. Two-pixel geometry and texture boundary bands are fixed before any
guest run. Robust interiors use (sum lambda*UV/W)/(sum lambda/W). A separate
object-space ray/plane intersection and dot-product barycentric calculation
agrees at interior grid samples. Constant W agrees with affine interpolation;
uniform W scaling preserves the expected texture. Wrong affine captures,
background-only, shifted-stage, extent, source and interior-pixel mutations
are rejected. See coverage001.json for disjoint affine/perspective regions.

Five host tests pass. Source/test snapshots are retained here. This is only a
host reference, not a Windows or Xbox result. New 556 will compile a standalone
sample with explicit texture-perspective state set/get and fresh NT5 control.
Existing combined-scene/loop source and oracle remain unchanged.
