# NT5 graphics ladder

Original MIT-licensed user-mode samples. Start with
[the sample guide](../../../docs/graphics-samples.md) for the ladder, build command,
run instructions, output interpretation and current qualification limits.

- `ladder.c`: runnable GDI reference, DirectDraw inventory and system-memory copy.
- `run.cmd`: records the actual exit code; refuses reused result prefixes.
- `present.c`, `sprites.c`, `lifecycle.c`: DirectDraw presentation, pixel formats
  and bounded resource-lifetime controls.
- `discovery.c`, `triangle.c`, `texture.c`, `depth.c`: D3D7 software inventory
  and offscreen rendering controls.
- `blend.c`: alpha-blending diagnostic. Its first NT5 PC run fails the exact
  transparent/opaque endpoint checks by one color level; see the sample guide.
- `d3dpresent.c`: windowed D3D render, cover, move and expose checks.
- `transform.c`: six XYZ world/view/projection and viewport controls.
- `scene.c`: combined offscreen XYZ, two textures and depth/order controls.
- [Builder](../../../tools/build-graphics-samples.py): fresh out-of-tree RosBE build.
- [Independent checker](../../../tools/graphics_sample.py): report and pixel oracle.

No game assets, driver binaries, Windows DLLs or automatic console deployment.
Later ladder rungs are explicitly planned; they do not return placeholder PASS.
