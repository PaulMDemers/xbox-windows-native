# Saved PnP token lifetime observation

This kit continues the late installer investigation from
[shutdown-createprocess](../shutdown-createprocess/README.md). It uses that kit's
exact immutable owned input disk, matching Windows binaries, FATX0098, video0096
and the reviewed 120-second diagnostic helper. It does not modify the physical
Xbox, registry/device policy or driver payloads. Each numbered case is a unique
Windows launch under an owned emulator runner; reattachments never relaunch it.

The saved token global and interior observation sites are pinned to umpnpmgr.dll
from the owned archive. `sites.py` preserves the instruction bytes and surrounding
disassembly. Interior sites record registers, stack words and the current saved
token/mutex values, without inventing API arguments or return addresses.

The tracer records services.exe CloseHandle calls only when their argument equals
the current saved token. Installer creation is restricted to the umpnpmgr caller
or an already active call on the same thread. Native token-query/duplication and
process-information returns are armed during active creation. API returns are
paired by thread and return address; a numeric handle alone is not object identity.
Unreadable code/global values are retained as unknown rather than forced resident.
Software breakpoints and stepping alter scheduling even when no guest data,
registers or results are intentionally changed.

Use `Run.ps1 -Case 001` for the owned emulator, `supervise.py 001` with local FTP
credentials in XWN_EMULATOR_FTP_USER/PASSWORD for its single launch, and the shared
`capture-runtime.py --port 4594 --output .../001/runtime.json` once NT is running.
Preserve early undecodable captures separately. Save an exact trace-source.py
copy before `trace.py 001`. After supervisor return and runner cleanup, `audit.py
001` performs the read-only cold audit in the existing WSL/hivex environment.
Never rerun a used case ID or treat an uncertain launch as permission to retry.

Cold audits compare event deltas, normal shutdown, helper completion, exact
payload/binary hashes and five traversable hives. Known recurring baseline
SCM7000/Ftdisk49 signatures stay in the reports. These bounded diagnostic checks
are not the strict physical soak gates or a complete filesystem allocation audit.
The physical soak3 failure, FATX0098/video0093 and immutable0.1.0 remain preserved.
Actual outcomes and unresolved questions belong in summary.json and continuation.

## Completed observations

Both one-shot boots completed helper execution, normal shutdown and dashboard
return. Cold payload/binary/hive and bounded event checks passed, without a new
popup. They are not ordinary boot qualifications or fixes. The early001 runtime
capture was taken before the NT kernel was identifiable and is retained separately.

Run001 captured76 events. It observed a successful first01B0 installer creation
using token0x770. During the later01B4 attempt, the installer checked that token
was nonzero, then a different services.exe thread handled control5, successfully
closed0x770 and cleared the saved global. The installer subsequently supplied
zero to CreateProcessAsUserW. Native queries returned0xc0000008; inner process
creation still succeeded, but subsequent token setup failed and the wrapper
removed the child and returned last-error6. Events49–66 preserve that ordering.

Run002 omitted the generic CloseHandle observer, reducing ignored breakpoint hits
from25113 to51. It captured75 events, including the successful first01B0 launch.
The later01B4 call supplied a valid token0x908, and its initial native query
succeeded. While inner creation was active, another thread closed that token
and cleared the global. Inner creation returned success; the subsequent native
query of0x908 returned0xc0000008 and the wrapper again failed with last-error6.
Events49–65 record this different interleaving of the same lifetime problem.

The local pinned SDK header identifies0xc0000008 as STATUS_INVALID_HANDLE and
0xc0000023 as STATUS_BUFFER_TOO_SMALL. The earlier successful launch includes
zero-buffer size queries followed by successful allocated-buffer queries;
those expected size probes must not be mistaken for its failure.

The traces locate the close within umpnpmgr's control callback, rather than just
inferring a stale handle from numeric reuse. They do not establish uninstrumented
frequency or the cause of the actual DLL-initialization popup. No driver change
or binary patch is justified as a popup fix from this evidence alone. The next
experiment should correlate that exact hard error with the originating installer
in the previously failing workload, retaining this clean-failure path as a control.
Any eventual fix must prevent new installer work during shutdown and protect the
token through its complete use; a second nonzero check alone leaves a close-during-
creation window. That is a design constraint, not an implemented or qualified fix.
