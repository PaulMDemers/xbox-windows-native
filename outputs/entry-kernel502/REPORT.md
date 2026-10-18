# Early kernel file boundary502

The exact499 early-entry file path passes a fresh isolated emulator test. The
actual Xbox kernel accepts create,96-byte write,flush,16-byte write,flush and close,
with zero returned status, expected IOSB values and correct stdcall stack cleanup.
This does not explain physical501, which still produced no early or Windows file.

One local emulator SITE request at08:43:32.438969UTC returned200. The trace ended
08:43:35.034265UTC with14 checkpoints and70 retained private captures. All648 gate
bytes,236 initial data bytes and64 original-start bytes matched reviewed499 XBE
22d3a9224965159a53cb188be9530f1b211aff8480d3d5773405d7e2974cf6d9.
The loaded header was retained, not asserted byte-identical across mutable loader
fields. This run did not compare the entire payload or execute the old preparation.

All eight resolved thunks match the actual kernel export table: base80010000,
size636160,timestamp1023192752,366 exports. Actual control registers, segments,
descriptor tables and code/data/stack/create-handler translations were captured;
virtual and physical bytes agree. Kernel header/export identity plus pinned BIOS
is not a full symbol-matched kernel image or physical-console kernel qualification.

Create returned handle8 and IOSB0/2. Writes returned0/96 and0/16; both flushes
returned0/0 and close returned0. State7 was observed at the original start before
its first instruction, with original registers and flags restored. The112-byte
memory receipt independently decodes and exactly matches the cold file. The
receipt decoder correctly retains its own limitation: receipt contents alone do
not prove final flush/close; those are separately established by actual call stops.

The host parser checks12 accepted contracts and48 mutations. Actual observer
sequencing passes51 modeled transport-failure boundaries and21 negative cases.
Host002 incorrectly expected a different valid nonzero opaque handle to fail;
its original failure is retained. Host003 changes only that negative to zero.
Independent actual-evidence review rejects96 call-record mutations and112 receipt
byte mutations without changing the original captures.

All breakpoints were removed, physical-memory mode restored, and owned host
stop/quit exited0 without fallback. The complete10,000,000,000-byte virtual mapping
and327680 child-local bytes were compared. Strict equality is FALSE:275 bytes
changed, including diagnostic persistence and reserved/header-area bytes; writer
attribution for every changed byte is not established. Allocation audit reports
276 directories,6554 files,255 directory clusters,zero errors/orphans. Five hives,
three protected baseline binaries, seed and EEPROM remain byte-identical.

No Windows execution, normal guest shutdown, ordinary boot, physical reliability,
D3D/game/performance or release qualification is claimed. No physical access,
startup hook, SDK or functional driver change occurred. The fixture is a new child
of never-executed466 preparation, not a closed runtime. All owned processes closed.
The initial continuation-writing command failed cp1252 decoding before mutation;
the runner still started, and the note was corrected with explicit UTF8. The
original failure is recorded separately; no launch was retried.

See emu001/trace.json, audit.json, protected.json, actual-review001.json and
final-review.json.246 frozen repository inputs and17 external inputs remain exact.

Final review rehashed404 private files; all owned processes are closed. Repository
check30098 passed37578 tracked files. Initial Git whitespace check classified
preserved CRLF as trailing whitespace; cr-at-eol was added to this kit, matching
preceding frozen kits. No evidence was normalized; exact staged bytes were checked.
