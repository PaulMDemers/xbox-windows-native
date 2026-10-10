"""Fresh232 kit; all231 runtime/source records stay immutable."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'xemu-backend-publication231';dest=k/'author.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inputs={}
for name in ['common.py','typed-state.py','prepare.py','Prepare.ps1','Run.ps1','Invoke-231.ps1','run-emulator.py','supervise-emulator.py','trace.py','audit-emulator.py','test-guards.py','freeze.py','Build.ps1','build.py']:
    p=old/name;inputs[str(p.relative_to(ws)).replace('\\','/')]=sha(p);s=p.read_text()
    s=s.replace('publication231','consume232').replace('Invoke-231','Invoke-232')
    s=s.replace('xemu-backend-publication231','xemu-backend-consume232')
    if name=='build.py':
        s=s.replace('xemu-backend-reason228','xemu-backend-publication231').replace('candidate002-source-pins.json','candidate001-source-pins.json').replace('artifacts/build002/source','artifacts/build001/source')
        s=s.replace("'hw/xbox/nv2a/pgraph/gl/surface.c']", "'hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pfifo.c']")
        s=s.replace("names+['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/nv2a_regs.h']", "names+['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/nv2a_regs.h']")
    if name=='freeze.py':s=s.replace('xemu-backend-dashboard230/emulator-frozen.json','xemu-backend-publication231/emulator-frozen.json')
    if name=='trace.py':
        s=s.replace('publication_version\']==231','publication_version\']==232')
        s=s.replace('|old_halt|request[0-9]', '|old_halt|consume_stop|consume_steps|consume_words|wait_before|wait_after|request[0-9]')
    if name=='audit-emulator.py':s=s.replace('231 uses','232 retains231 and uses')
    q=k/('Invoke-232.ps1' if name=='Invoke-231.ps1' else name);assert not q.exists();q.write_text(s)
    if q.suffix=='.py':ast.parse(s,filename=str(q))
for n in ['gdbstub/gdbstub.c','gdbstub/system.c']:
    p=old/'source'/n;q=k/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
dest.write_text(json.dumps(dict(parent_inputs=inputs,actual_compiled_model_stub_pins={n:sha(k/'source'/n) for n in ['gdbstub/gdbstub.c','gdbstub/system.c']},physical_access=False,guest_launch=False),indent=2)+'\n')
(k/'DESIGN.md').write_text('''#232 finite actual FIFO consumption, emulator only

One stopped-dashboard request; actual existing pusher/puller with budgets:
32768 iterations,32768 committed words, inherited5sec real-time deadline.
Cap lookahead to the remaining word budget. Ordinary calls use NULL and retain
the existing parser, assertions and lock transitions. Diagnostic bounds never
write a synthetic GET, clear error/wait state, toggle halt or resume producers.
Raw wait bits1PGRAPHaccess-off/2nop/4flip/8context; before/after capture. Real
wait flags conservatively refuse before dispatch. CPU remains paused under the
owned host monitor/GDB phase until genuine terminal refusal/preservation; no
native/upstream ownership contract follows from this host-only protocol.
Release/acquire terminal publication and timeout tuple withholding retained.
Stop codes in the actual source; invalid range/count/parsererror quarantine.
GL calls are not fully cancellable: independent owned host bound retained.
Preserving dirty readback and ended references remain separate gates. Native
allocator/private-context/CPU-alias gates are unchanged. No physical access.
''')
(k/'NEXT.md').write_text('Inspect actual232 consume result and raw wait/queue words. No native grant.\nNever rerun closed cases; preserve refusal/failure and cold audits.\n')
print('232 fresh bounded-consumer harness authored')
