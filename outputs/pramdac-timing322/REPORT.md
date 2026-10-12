#322 emulator timing storage compiled

The exact11340-file qualified emulator source was reconstructed before changing four files. Three PRAMDAC registers now retain writes: VTOTAL804, VSYNC_START80c, HTOTAL824. Values initialize on reset and are appended as VMState version4 fields, with legacy pre-load initialization. The guest316 loader and all validation gates are unchanged. No raster/field timing simulation is added.

Actual read/write function host tests pass409614 assertions each for control and candidate under ASan/UBSan. They demonstrate the original zero readbacks and corrected ordinary value storage/isolation. The containing device and logging are modeled. Migration schema is reviewed and compiled, not exercised through actual save/restore.

Matched build003 used the pinned GCC toolchain. Control executable text is byte-identical to the prior qualified emulator. Candidate changes only the reviewed four files; all six borrowed source files are restored. Incremental compilation produced46 control and four candidate warning instances, all inherited messages. Build hashes and private source manifests are in final-review.json.

Failures preserved: build001 host stub discarded logging arguments and triggered unused-parameter compilation failure; build002 corrected stub passed tests, then rootless Podman failed before compiling xemu. Build003 uses the established root container toolchain and reuses the byte-identical passing host002 inputs rather than rerunning them.

New323 ordinary guest qualification is separate. Nothing was deployed to the physical console; 0.2.0 remains untagged.
