# Concurrent close of the installer's supplied token

Fresh candidate001 captured a successful cross-thread close of the exact token
being used by `CreateProcessAsUserW`. This localizes this observed installer
failure to a handle lifetime race. It does not establish the producer of the
separate intermittent shutdown popup or explain the original physical FATX
damage. No guest code, driver, setting, device policy, UI, or physical console
was changed.

The single launch was accepted at 2026-10-09 01:18:16.223896 UTC and returned to
the emulator dashboard at 01:20:43.532667 UTC. Runner84735, tracer49818,
supervisor86204 and cold audit27084 are CLOSED. The observer captured222 events,
201 resident code pins,27 creation pairs and82 native API pairs. All pairs use
actual ETHREAD and disassembly-verified stack deltas; no pending returns remain.
All breakpoints were removed and the guest resumed. Five unreadable hits remain
explicitly unknown. Diagnostic capture is complete within the declared scope.

## Captured sequence

All rows refer to the same `services.exe` owner EPROCESS4266433344, PID208,
outer call189 and supplied token handle1880, command `rundll32.exe
newdev.dll,DevInstall PCI\VEN_10DE&DEV_01B4...`.

| Events | Thread | Tick | Observed result |
|---|---:|---:|---|
|189|4290179104|6621|UMP calls CreateProcessAsUserW with token1880|
|190/191|4290179104|6621|Token query class12 succeeds, four output bytes00000000|
|192|4290179104|6621|Inner CreateProcessInternalW starts|
|199/202|4288548896|6624|User NtClose(1880) returns status0|
|200/201|4288548896|6624|Nested live-kernel NtClose(1880) returns status0|
|209|4290179104|6631|Inner creation returns TRUE, handles1904/1892, child732/thread936|
|210/211|4290179104|6631|Query token1880 class8 fails STATUS_INVALID_HANDLE C0000008|
|220|4290179104|6631|Outer creation returns FALSE, LastError6|

The closing thread differs from the installer thread, but has the same owner
EPROCESS. Both close pairs returned successfully before the failing query. The
immediate user close caller is resident-pinned `kernel32!CloseHandle`: export
RVA32417, return RVA32496, pin185, exact matching owned binary SHA256
6b05b0749b5dd86da94cc4acd062ca05472509f70216b56cd4a5b9809c602e73.
`verify-token-race.py` checks the sequence, process/thread/handle identities,
paired statuses, actual export and cold bytes independently of the recorder.

No higher closing-thread frame was captured. Do not name its cleanup callback,
claim a specific token object's deallocation or infer arbitrary attached-process
handle contexts. The live kernel dispatch pin is verified; its immediate return
caller lacks a user-loader identity and stays unknown. The observation proves
the successful concurrent close and subsequent invalid-handle use, not an
ordinary-run reproduction frequency or a physical failure cause.

## Unchanged workload and cold checks

Five samples,20 pixel-copy checks,25 timed loops and50 full-scan RAM/framebuffer
RGB coherence checks passed. Normal shutdown/dashboard returned. Complete cold
allocation:322 directories,6721 files,323 directory clusters,zero errors/orphans.
Five structural hives, protected files and staged startup bytes passed.

Strict qualification remains FALSE for the exact inherited Ftdisk49 error on
HarddiskVolume6. No application-event delta or popup occurred in this run. The
popup captured in174/173/172 remains unresolved;175 also had this token failure
without a popup. Error6 and the shutdown DLL-initialization popup are separate
observations. Debugger results are not ordinary or physical qualification.

## Source provenance and host review

The final runtime recorder/source snapshot and51 frozen pins matched exactly.
Current host tests passed6 identity/resident-code cases,5 close-scope cases and5
shared-return-scope cases. Early176 tests and `api-scope-review.json` refer to
the initial pre-return-selector implementation, preserved byte-exact as
`trace-before-return-scope.txt` and `scope_match-before-return-scope.txt`.
Their hashes are deliberately not rewritten to pretend they describe the final
source. Final `trace.py` and `scope_match.py` have separate current002 tests and
frozen source pins. `create-kit.py` reproduces the initial implementation; the
final frozen sources are the authoritative launch inputs.

The offline cross-case review initially refused an incorrect assumption that
informational popup type4 rows were in `warnings_errors`. No output or guest
operation resulted. Its source/refusal are retained; corrected read-only review
checks both collections and the unchanged strict popup gate. This is a host
review failure, not a guest result. `evidence-review.json` verifies all four
closed173–176 cases, exact frozen sources, audit/cleanup hashes and this race.

Physical FATX0101/video0093, original0088 rollback and immutable0.1.0 are
unchanged. No physical FTP, deployment or test occurred. C: free space after
closure was21690884096 bytes, close to the unchanged20GiB guard; recover capacity
from verified closed standalone artifacts before any substantial new child.

Next: identify the higher closing-thread caller and the token owner lifecycle,
then design a genuine lifetime/synchronization fix. Independently capture the
shutdown popup producer; never hide it by disabling PnP, services, events or
automatically dismissing a wizard. Preserve all closed cases and their failures.
