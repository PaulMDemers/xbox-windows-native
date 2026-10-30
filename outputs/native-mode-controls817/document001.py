"""Preserve host evidence and exact launch continuation; no hardware access."""
from pathlib import Path
import json,hashlib,zlib,base64,datetime
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(n,s):
 with (K/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
raw=(K/'prefix002.json').read_bytes();packed=base64.b64encode(zlib.compress(raw,9))+b'\n'
assert zlib.decompress(base64.b64decode(packed))==raw
put('prefix002.json.zlib64',packed.decode())
put('receipt-storage001.json',json.dumps(dict(raw_file='prefix002.json',raw_sha256=sha(raw),raw_bytes=len(raw),public_lossless='prefix002.json.zlib64',encoding='zlib + base64',public_sha256=sha(packed),raw_retained_locally=True),indent=2)+'\n')
head='''# Native817 launched once; held report pending

One SITE accepted at 2026-10-30 02:00:22 UTC after authenticated dashboard001,
exact source/build checks and unique E staging/readback. Native hold intended;
actual color, execution outcome and power-cycle/dashboard return not yet observed.
No second launch. No startup hook or Windows launch. All12 host CPU VMs closed.
Expired automation remains paused; user renewed tonight work toward desktop.

Next: obtain the fresh817 photo and reported power-off/on; independently
authenticate dashboard before collecting nine preparation phases once. Decode
against optical-schema001: seven cleanup masks and one forward mask;27 additional
cleanup masks aggregate-only. CR1A raw rows are before, after, then AFTER CR2D
undo BEFORE own undo (expected38/3C/3C). The last row is NOT final restoration.
Final own CR1A restore is aggregate-only through the strict cleanup/final status.
After qualified817 closure, admit a combined visible-mode test, then Windows
handoff. Complete native visible mode and Windows1.6 desktop remain unproved.

Fresh917-word native payload mirrors CLOSED816 except native CPU guard. Its
40KiB allocation/ten alias pages, larger payload/result/IDT/stack regions were
independently checked before staging. Closed813/816 reused as pinned source only.
Tail002 stale CPU-checker failure and WSL/Windows-Unicorn invocation failure are
preserved; corrected tail003 passes146 cases. No waiver or driver modification.

'''
put('NEXT.md',head)
for n in ['CONTINUATION.md','STATUS.md']:
 p=W/'outputs/engineering-notes'/n;p.write_text(head+p.read_text(encoding='utf-8-sig'),encoding='utf-8',newline='\n')
put('README.md','''# Native817 preserving mode-control qualification

This fresh diagnostic extends the native prefix with kernel816's qualified
CR1A bit2-only control, followed by CR25/CR28/CR2D. CR1A target is saved OR04;
the measured kernel transition was38 ->3C ->38. All ten neighbor bytes are
compared at each step and restoration runs in reverse before restoring the
entire prefix. Raw04/read2C failed815 remains closed and is not waived.

No complete visible native mode or Windows desktop claim. Same-value CR25,
CR28 and CR2D writes do not prove effective writes. The held optical result is
required for native evidence; disk reports stop at kernel handoff preparation.

## Layout and verification

40KiB owned allocation: bridge0000..0900, payload0900..77C0, request77C0..77FC,
917-word result7800..8654, IDT8700..8F00, stack8F00..A000 (4352 bytes).
Ten physical alias pages and endpoint translations are checked. Unused GDT
descriptor08's low word is corrected to offset808; active selectors10/18
remain unchanged. Raw payload24744 bytes, reserve28352,53 relocations41 absolute.

Host checks:1014 prefix outcomes,146 tail fault cases,54 relocated integration
cases,76 optical cases,12 diskless CPU fixtures closed,164177 plan cases,
418 compiled plan cases,60+61 compiled page cases,823 schema corruptions.
Compiled tested bytes are checked in both PE and XBE. Source-review001 verifies
the sole CPU guard delta from816 and reverses bitmap/recovery compaction exactly.
These checks are host evidence, not physical video or Windows proof.

tail002 retains a stale kernel-CPU expectation failure; tail003 corrects that
checker only. invocation-failure001 records an incompatible WSL Unicorn import,
before any execution; the Windows checker and WSL CPU fixtures subsequently pass.
Earlier page-review generator revisions were not executed;010 separates the
larger payload buffer from relocation metadata and checks the full40KiB output.
Some inherited descriptions still say horizontal/32KiB/eight pages/707/COFF;
active code, manifests, tests and review001 establish the actual817 layout.

## Optical evidence contract

13 rows: signature, final code,7 cleanup masks,1 forward mask, CR1A before,
CR1A after, CR1A after undoing CR2D but BEFORE its own undo. Expected success
raw bytes38/3C/3C. Do not label the last row final restoration.27 additional
cleanup masks and final own restoration are aggregate-only. Preserve photos
privately and bind decode/review to their hashes.

## State and reproduction

See NEXT.md. One accepted SITE at02:00:22 UTC; no repeat or collection yet.
Private build and runtime files are under C:/xwn817; no proprietary payload,
photo or credential is published. Prefix002 is stored losslessly as zlib/base64;
receipt-storage001 gives the original hash. Reconstruct that JSON when reviewing
the frozen manifest, without running a closed fixture.

Generators prepare001/002/003 are historical derivations, not rerun commands.
Fresh reproduction requires a new attempt namespace/private directory and new
leases/receipts. Active flow: payload_build008, host_build009, cpu006 build/run,
prefix002/tail003/integration001/optical_review005, build015, page_review010,
page_boundary010, plan_review003, link_review012/linked_review007, independent
schemas/controller/source reviews, freeze001, then bounded physical009.
Never relaunch/recollect/runtime-parent a closed attempt.
''')
put('process-state001.json',json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_CPU_VM_count=0,all_12_CPU_closed=True,owned_host_processes=[],console='Native817 accepted; deliberately held report pending observation',launch_count=1,hook=False,windows_launched=False,automation='PAUSED',next='Photo and independent dashboard authentication, then one collection'),indent=2)+'\n')
print('817 continuation and lossless prefix evidence preserved')
