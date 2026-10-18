# 493 PC D3D transform control: closed, scoped PASS

Both default and forced HEL paths passed six unlit D3D7 RGB software controls:
identity, world translation, view translation, rotation followed by view
translation, perspective divide, and a displaced viewport. Actual XYZ vertices
were submitted to D3D; this is not an XYZRHW or host-generated pixel test.
The independent Fraction oracle was fixed before build and launch.

Each process produced two 98,304-byte captures. Across both paths the checker
examined 393,216 captured bytes, including 294,912 RGB bytes. The unused high
color byte and pitch padding are excluded. Interior and exterior colors must
match exactly; the predefined two-pixel edge band permits foreground/background
only. The result field `exact_capture_bytes` denotes stream length, not exact
coverage of the high byte or exact raster edge placement. Matrix, viewport,
vertex, state, format and ownership records also passed independently of pixels.

One fresh qualified 404 seed child launched under the owned emulator lease.
The guest completed both bounded cases and restarted normally at
2026-10-18 06:47:17 UTC; QEMU exited zero without watchdog deadline, host quit or
kill. Cold enumeration found 6,485 files and 309 directories, five clean hive
headers and a normal-shutdown event delta of one. The selected new system event
records are EventLog 6006/6009/6005, with no warning/error in that delta.
This is not a full NTFS allocation/ownership audit; the inherited SOFTWARE typed
DRM decoding limitation remains explicit.

An independent NTFS-3G reader agreed with the first reader. Eleven live module
records per process were joined to independent cold file bytes and installed
pins. The snapshot does not describe previously unloaded modules. Actual-result
negative controls rejected 616 metadata and 108 pixel mutations per path
(1,448 total); original captures/reports remain unchanged. All 149 frozen inputs
were archived and rehashed. See final-review.json for every private file hash.

Actual sample: 22,745 bytes, SHA256
02b6e4191b07eaccfe1dc199655a9deb1292e6e45341bf2a72c56fd2b25f8eca.
Runner: 12,958 bytes, SHA256
 d1a585795f7507a4655ea893c3cfaf82b97158f371694cb2329ee5de0df33a68.
Public builder output has all five PE sections byte-identical to the executed
sample; header OS version/timestamp differ. It was not separately executed.
Both compile logs are empty and actual NT5 static import checks pass.

Host oracle001 failed because unchanged identity could pass two insufficiently
distinct geometries. Oracle002 failed the unchanged minimum interior-area gate.
Both sources/results were preserved privately before correction. Oracle003
passes four groups with stronger geometry and unchanged tolerances/minimum
coverage, selected before any runtime. No expected pixels were fitted to a
failed guest capture. No consumed attempt was rerun.

No physical console access, startup hook, driver or SDK change occurred in493.
Runtime55802, baseline43492, cold/review70670 and all helper processes are closed.
The console was last recorded at dashboard after492, with its hook removed.
No Xbox transform, clipping, lighting, combined scene, GPU, performance or game
qualification follows from this result. Earlier physical Ftdisk49, shutdown
popups and intermittent boot failures remain unresolved.
