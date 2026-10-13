# Release and emulator inputs recovered on E:

The missing Windows paths did not require a new video build. Retained WSL
build outputs supplied byte-identical720p/1080i launchers, the303 display DLL
and322 emulator. All were copied to E:/xwn329/retained-builds001 with matching
source and destination SHA256. The earlier C:/E: inventory had not inspected
those native Linux build directories.

The recovered package is at
E:/Codex-archive/xbox-windows-native/0.2.0-recovered329.
The HD overlay and30965-entry source archive exactly match their original
whole-ZIP hashes. Every entry of the combined demo/recovery ZIP matches the
original; its outer hash differs. The regenerated Git history bundle verifies
both immutable release tags and complete ancestry, with new pack bytes.
Original tags, package evidence and qualification limits are unchanged.
START-HERE.md provides current E: paths and the guarded deployment workflow.
No physical-console access, install, recapture or restore occurred.

The313 helper was freshly compiled from exact pinned sources/tool/flags.
Its first binary differed. A bounded reconstruction changing only the COFF
timestamp and PE checksum reproduced the original full binary SHA256 exactly.
Four changed metadata bytes are recorded; the initial compile remains intact.
No approximate binary match was used.

The missing317 QCOW container was not recovered byte-for-byte. A new
never-executed fixture was reconstructed from retained251 with seven exact
HD/helper replacements. Full E:/F: comparison checked6795 files and339
directory entries: precisely seven file contents changed, every other byte of
file contents and every entry's name/attribute/timestamp metadata was unchanged.
All original317 protected/file pins match. Full F: allocation is clean:
322 directories,6752 files,323 directory clusters,zero errors/orphans.
Five hives parse. The new standalone disk matches its preparation child by
qemu-img compare and passes qemu-img check. Its distinct container hash is
explicit and it has never run. No executed disk was used as its parent.

The first full-file enumerator incorrectly followed a valid empty directory
whose first cluster is zero. Its read-only refusal and source hash are preserved
in content-failure001.json; corrected verifier002 skips traversal of that empty
directory while retaining and comparing its metadata. No disk was changed by
either verifier. The complete passing comparison is content-review002.json.

330 is the separate next benchmark kit. It replaces only replay.exe with the
compiled327 large-area probe on a child of this new verified fixture. Its runtime
results cannot be inferred from this artifact recovery or from older323 runs.
