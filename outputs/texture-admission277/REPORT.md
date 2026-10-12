#277: proposed lifetime-aware texture admission tested on the host

The proposed texture-only observation rule keeps the four known dirty surface
callbacks intact and rejects unknown owners or any overlap with the four complete
test texture allocations. An actual-list mutation clock catches remove/reinsert
activity even if pointers and ranges return to their original values.

host002 passes20,771 ASan/UBSan checks,4096 exact actual insert/unlink/free pairs
and1024 pthread publication races. Original callback function bodies reconstruct
exactly after removing the added metadata calls. No renderer build, guest launch,
release or physical change occurred. Private exact inputs/executable are under
E:/Codex-archive/xbox-windows-native/admission277-host002. host001 is preserved.

The276 data is used only as a model seed. Its missing second CPU acknowledgment
and mutation clock still cause refusal; its observation PASS, admission FALSE
and reserved-disk-byte strict failure remain unchanged. Two unbound surfaces'
native allocation provenance remains unknown. They may remain untouched outside
this narrow texture observation; this grants no backend or native GPU ownership.

Next implement the actual opt-in adapter with both CPU acknowledgments, full
immutable proof transport and delayed observer arming, then test actual worker
failure paths before a fresh emulator control. A host struct with plausible
values is not sufficient runtime evidence. Read DESIGN.md for precise scope.
