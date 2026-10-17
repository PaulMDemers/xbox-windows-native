# Fresh physical E: FATX allocation check

The previous completed physical E allocation scan was October14 at19:49UTC
(case398):682 directories,7849 files,699 directory clusters, no errors/orphans.
Later boot checks verified selected files and registry hives, not full allocation.

On October17, fresh scan002 used the unchanged scanner341 executable
`66e58932a1c3cd647d8ffd7bec825835f4d92a8b337e40fffd7d7acea2249967`.
It reads native Partition1 only after checking its stock E start/length and16KiB
geometry. Reports are written beside its unique XBE on dashboard F. No raw writes,
repair, format, ATA operation, Windows launch, or dashboard C access occurred.
The native application's D alias means its own executable directory on F; it
is unrelated to host drive letters. Host artifacts use C/E only.

The scanner completed and returned to UnleashX. Complete FAT metadata and directory
records were downloaded twice and compared byte-for-byte before offline analysis:

- 722 directories,8063 files,739 directory clusters.
- 204937 allocated clusters;107487 free clusters (1761067008 bytes).
- Zero orphan clusters, allocation errors, capture-chain warnings, or marked bad clusters.
- Ten original boot/startup/hive/event/trace files unchanged from the462 closeout;
 protected720p payload verification also passed.

Five deliberately corrupted copies of this actual capture were rejected by the
unchanged analyzer: orphan allocation, freed directory root, crosslinked files,
file size exceeding its chain, and an invalid counted-name length. Original
captures remain exact. These controls run on host copies, not the console.

This is an allocation-consistency result for E. It is not a surface/media scan,
SMART diagnosis, complete file-content audit, fresh F allocation audit, Windows
boot-reliability result or repair. It does not clear the historical Ftdisk49 or
Srv2013 WindowsF warning. Historical mapping identifies that WindowsF volume as
dashboard C, which remains untouched.

Attempt001 timed out during prelaunch FTP double-read, before remote directory
creation or SITE EXEC. Its code/preflight/partial record and failure are retained.
Fresh attempt002 uses a separate namespace and45-second socket timeout; the native
scanner is byte-identical. Only one scanner launch was sent. All owned sessions
closed; no next console test queued. Private capture: E:/xwn463/scan002.

Evidence: [preflight](preflight002.json), [launch](trial002.json),
[return](return002.json), [collection](collection002.json),
[allocation](allocation002.json), [controls](verification001.json).
