# Rung03 Windows2000 PC control passed

Default and forced HEL each passed all four presentation stages: visible,
sibling-covered, moved while covered, and uncovered. Each case independently
matches1,802,240 source/before/after bytes. The clip lists contain1/4/4/1
rectangles with exact coverage. GDI guard and cover pixels remain intact;
the source pattern is never painted by the GDI handlers. Actual process exits0,
all recorded release counts0, no non-waiting API refusal or retry.

The new sample explicitly places the cover above its sibling and checks real
Z-order/visibility. Both processes initially observed `cover.preabove=0`, then
`cover.above=1`. This resolves the test setup missing from the separately
preserved [439 failure](../presentation439/REPORT.md); no driver was changed.

The exact sample is SHA256
`4f1abf4417620aee9c8343962042cc48cbd6c6abc37215a457acd08c2e310132`,
25,302 bytes. Pinned RosBE build is warning-free;45 imports match owned NT5
exports. Three independent-verifier test groups pass;468 mutations of actual
reports/pixels/lengths were rejected with original files unchanged.

The fresh child of404's closed NTFS installation booted once,640×480×16 Cirrus,
64MiB/noNIC, then requested a normal restart. QEMU exited0 without host quit,
deadline or kill. Cold audit enumerated6,487 files/309 directories, one new
EventLog6006 and unchanged protected Windows binaries; QCOW check passed.
Independent NTFS3G reads agree for22 selected files, view unmounted, disk unchanged.
Five hives retain clean headers/raw-value agreement; unknown typed SOFTWARE DRM
data remains. This is not a full NTFS allocation audit.

See [actual review](runtime-review001.json), [negative controls](actual-controls001.json),
[cold audit](ntfs-cold1-002.json), [independent reader](independent001.json),
and [final closure](final-review.json).137 exact inputs are archived privately,
along with the consumed child/captures under
`/home/paul/xbox-windows-native/presentation440-*`. Never relaunch or parent it.
No proprietary pixels, DLLs, hives or executables are committed.

This proves owned source and GDI-observed primary presentation in this PC
fixture. It does not prove physical scanout, GPU execution, performance or D3D.
