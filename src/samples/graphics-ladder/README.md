# NT5 graphics ladder

Original MIT-licensed user-mode samples. Start with
[the sample guide](../../../docs/graphics-samples.md) for the ladder, build command,
run instructions, output interpretation and current qualification limits.

- `ladder.c`: runnable GDI reference, DirectDraw inventory and system-memory copy.
- `run.cmd`: records the actual exit code; refuses reused result prefixes.
- [Builder](../../../tools/build-graphics-samples.py): fresh out-of-tree RosBE build.
- [Independent checker](../../../tools/graphics_sample.py): report and pixel oracle.

No game assets, driver binaries, Windows DLLs or automatic console deployment.
Later ladder rungs are explicitly planned; they do not return placeholder PASS.
