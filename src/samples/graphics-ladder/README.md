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
- `scenepresent.c`: combined scene with clipped window presentation (PC validated; Xbox pending).
- [Builder](../../../tools/build-graphics-samples.py): fresh out-of-tree RosBE build.
- [Independent checker](../../../tools/graphics_sample.py): report and pixel oracle.

## Find the source, runner and checker

Pass the name in the first column to the builder's `--sample` option. The
builder copies that source and runner into a fresh output directory alongside
the executable and build receipt. Copy the executable and runner together to
Windows; the Python checker runs on your PC after you retrieve the results.
See the guide for each sample's arguments and required capture files.

| Build selection | Source | Windows runner | Host checker |
|---|---|---|---|
| `ladder` (default) | [ladder.c](ladder.c) | [run.cmd](run.cmd) | [graphics_sample.py](../../../tools/graphics_sample.py) |
| `present` | [present.c](present.c) | [present.cmd](present.cmd) | [graphics_present.py](../../../tools/graphics_present.py) |
| `sprites` | [sprites.c](sprites.c) | [sprites.cmd](sprites.cmd) | [graphics_sprites.py](../../../tools/graphics_sprites.py) |
| `keyprobe` | [keyprobe.c](keyprobe.c) | [keyprobe.cmd](keyprobe.cmd) | [graphics_keyprobe.py](../../../tools/graphics_keyprobe.py) |
| `lifecycle` | [lifecycle.c](lifecycle.c) | [lifecycle.cmd](lifecycle.cmd) | [graphics_lifecycle.py](../../../tools/graphics_lifecycle.py) |
| `discovery` | [discovery.c](discovery.c) | [discovery.cmd](discovery.cmd) | [graphics_discovery.py](../../../tools/graphics_discovery.py) |
| `triangle` | [triangle.c](triangle.c) | [triangle.cmd](triangle.cmd) | [graphics_triangle.py](../../../tools/graphics_triangle.py) |
| `texture` | [texture.c](texture.c) | [texture.cmd](texture.cmd) | [graphics_texture.py](../../../tools/graphics_texture.py) |
| `depth` | [depth.c](depth.c) | [depth.cmd](depth.cmd) | [graphics_depth.py](../../../tools/graphics_depth.py) |
| `blend` | [blend.c](blend.c) | [blend.cmd](blend.cmd) | [graphics_blend.py](../../../tools/graphics_blend.py) |
| `d3dpresent` | [d3dpresent.c](d3dpresent.c) | [d3dpresent.cmd](d3dpresent.cmd) | [graphics_d3dpresent.py](../../../tools/graphics_d3dpresent.py) |
| `transform` | [transform.c](transform.c) | [transform.cmd](transform.cmd) | [graphics_transform.py](../../../tools/graphics_transform.py) |
| `scene` | [scene.c](scene.c) | [scene.cmd](scene.cmd) | [graphics_scene.py](../../../tools/graphics_scene.py) |
| `scenepresent` | [scenepresent.c](scenepresent.c) | [scenepresent.cmd](scenepresent.cmd) | [graphics_scenepresent.py](../../../tools/graphics_scenepresent.py) |

`blend` still tests the original ideal alpha endpoints; the separate arithmetic
characterization does not turn its failed endpoint result into a pass. `scene`
has completed Windows 2000 PC and Xbox offscreen comparisons. The combined
windowed `scenepresent` sample uses the existing RGB32/RGB565/RGB555 desktop; PC validation passed and the Xbox comparison is pending. See the
[current ladder status](../../../docs/graphics-samples.md#the-ladder) before
interpreting a successful build as tested support.

No game assets, driver binaries, Windows DLLs or automatic console deployment.
Later ladder rungs are explicitly planned; they do not return placeholder PASS.
