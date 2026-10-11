#266 scoped ownership observation passed; retirement remains unqualified

The fresh emulator diagnostic completed two native attestations and one read-only
ownership capture. The guest verified32768 original CPU seed bytes across two
reads and zero writes, then completed the existing224 workload and restarted
normally. The host reopened the frontend, removed all breakpoints, restored
physical-memory mode0 and exited orderly with code0 and no fallback kill.

Launch accepted22:16:02UTC; trace closed22:17:06; controller/cold audit closed
22:18:17. All owned processes are CLOSED. Never relaunch or recollect this attempt.
No physical hardware access, driver deployment, renderer disposal or GPU grant.

## Actual owner evidence

The immutable renderer report contains55028 rows across215 pages; UI capture
contains1807 rows across eight pages. Both CPU-exclusive inventories acknowledged
completion and contained zero callbacks, consistently before/after. There were
no pending predicate bits, capacity overflow or reference-accounting mismatch.
First pages and terminal report reread exactly as bytes. Independent analysis
verified every page index, epoch, row count and row shape. Twenty mutations of
actual reports were rejected in addition to the19 synthetic parser controls.

- 24 distinct texture bindings have24 cache edges and four additional unit edges.
 All four units are disabled yet retain a counted binding, refcount2 each. Their
 texture names are38/34/35/36. There are no unit-only bindings in this capture.
 This demonstrates the retained owners264 lacked; it does not demonstrate an
 executed finalizer leak because no finalizer or decrement ran in this test.
- All51200 allocated element-buffer names were captured;93 entries are live.
 Fourteen fixed objects,16 inline buffers,53 shader bindings and53 modules were
 recorded. Report/query queues are empty at this boundary.
- 54 shader actor records have UNKNOWN completion:53 save-thread handles and the
 loader. A retained handle is neither proof of a running thread nor a completed
 join. This diagnostic deliberately does not join or alter them.
- Actual UI HUD/snapshot/last-frame names are all26. The actual UI close report
 says fallback1 and glIsTexture live0. Renderer display texture is10. The UI uses
 the VGA fallback, whose ordinary source path deletes its temporary texture at
 the end of the frame, while HUD/snapshot numeric names remain. These are stale
 fallback names here, not demonstrated live aliases of the backend display.
- Continuing guest scanout conservatively reserves62914560..67108864. No release
 or ownership transfer follows from a closed frontend or zero loan count.

The first post-run analysis incorrectly asserted UI name==backend display name.
That script and its failure are preserved as actual-controls.py and
emu001/actual-controls-failure001.json. Corrected actual-controls002.py separately
classifies the actual fallback/live flags and source path. No raw evidence,
runtime gate or strict-event requirement was changed to obtain a pass.

Render/display role selections execute actual GL queries on the PFIFO worker and
restore active texture; UI records its actual SDL context/thread. The renderer
rows label the two roles but do not independently report their native context
handles. Indexed bindings and container attachments are also not complete.
These limitations and unknown shader completion prevent whole-backend retirement.

## Cold validation and boundaries

Cold allocation:322directories,6729files,323directory clusters, zero orphans and
zero errors. Five hives parse;31 protected hashes and selected device policies
match; event/setup history preserved.224 completed64leases,65allocations/releases/
refusals,3194880 verified bytes,128 preflight reads and four joined workers.
One EventLog6006 and dashboard return prove normal guest restart. Strict overall
qualification remains FALSE solely for inherited Ftdisk49. No event is waived.

Same renderer003 and native probe/driver as265; only the host recorder changed
to byte-exact UTF8 write/reread, with six transport cases and five changed-byte
rejections.2013 frozen inputs and108 host dependencies remain pinned. The source
is265's never-executed standalone preparation; the failed265 runtime disk is not
a parent.265 remains a failed interrupted case with13orphans/four WBEM errors.

This is debugger observation, not an ordinary build/performance qualification.
No acceleration,1080i, native GPU ownership or physical promotion is claimed.
Physical audio004/softwarevideo118/shared158/FATX0101, private recovery256,
immutable0.1.0/0088 and all rollbacks remain unchanged. The historical emulator
fixture retains its explicit synthetic null/unsupported-device policy and differs
from the current audio-integrated physical demo.
