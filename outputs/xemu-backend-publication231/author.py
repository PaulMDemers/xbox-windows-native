"""Create fresh231 runtime/build harness from closed230/228 byte-pinned parents."""
import ast, hashlib, json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'author.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=k.parent/'xemu-backend-dashboard230'
inputs={}
for name in ['common.py','typed-state.py','prepare.py','Prepare.ps1','Run.ps1','Invoke-230.ps1','run-emulator.py','supervise-emulator.py','trace.py','audit-emulator.py','test-guards.py','freeze.py']:
    p=parent/name;inputs[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
    text=p.read_text(encoding='utf-8')
    text=text.replace('dashboard230','publication231').replace('Invoke-230','Invoke-231')
    text=text.replace('../xemu-backend-reason228/artifacts/build002/xemu-preserve227.exe','artifacts/build001/xemu-preserve227.exe')
    text=text.replace('../xemu-backend-reason228/build002.json','build001.json')
    text=text.replace('xemu-backend-dashboard230','xemu-backend-publication231')
    if name=='trace.py':
        text=text.replace('(state|surfaces|dirty|downloaded|bytes|error|reason|references_retired|native_grant)', '(state|tuple_published|publication_version|surfaces|dirty|downloaded|bytes|error|reason|references_retired|native_grant|old_halt|request[0-9]|gate[0-9])')
        text=text.replace("assert r['preserve_result']['native_grant']", "assert r['preserve_result']['publication_version']==231\n assert r['preserve_result']['tuple_published']==int(state in [3,4,6])\n assert r['preserve_result']['native_grant']")
    if name=='audit-emulator.py':
        # A publication change is evidence only, never backend qualification.
        assert 'publication_contract_qualified' in text
    if name=='freeze.py':
        text=text.replace("xemu-backend-dashboard229/emulator-frozen.json", "xemu-backend-dashboard230/emulator-frozen.json")
    target=k/('Invoke-231.ps1' if name=='Invoke-230.ps1' else name)
    if target.exists():
        assert target.read_bytes()==text.encode('utf-8'), 'Partial author output differs'
    else:target.write_text(text,encoding='utf-8',newline='')
    if target.suffix=='.py':ast.parse(text,filename=str(target))
old=k.parent/'xemu-backend-reason228'
text=(old/'build.py').read_text()
text=text.replace("build002.json","build001.json").replace("xemu-backend-preserve227","xemu-backend-reason228")
text=text.replace("candidate005-source-pins.json","candidate002-source-pins.json").replace("artifacts/build005/source","artifacts/build002/source")
text=text.replace("artifacts/build002'","artifacts/build001'").replace('preserve227-build002.patch','publication231-build001.patch').replace('candidate002-source-pins.json\').write_text','candidate001-source-pins.json\').write_text')
text=text.replace("==sorted(n for n in names if not n.endswith('renderer.h'))", "==sorted(n for n in names if not n.endswith(('renderer.h','surface.c')))")
# Record all compiled atomic/parser source identities; host tests use these bytes.
text=text.replace("for n in names:\n  q=art", "for n in names+['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/nv2a_regs.h']:\n  q=art")
text=text.replace("sha(k/'candidate002-source-pins.json')", "sha(k/'candidate001-source-pins.json')")
assert "prior/'artifacts/build002/source'" in text
(k/'build.py').write_text(text);ast.parse(text)
text=(old/'Build.ps1').read_text().replace('xemu-backend-reason228','xemu-backend-publication231')
(k/'Build.ps1').write_text(text)
for n in ['gdbstub/gdbstub.c','gdbstub/system.c']:
    p=parent/'source'/n;q=k/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
(k/'DESIGN.md').write_text('''#231 ordered queue telemetry, emulator only

Fresh model child of exact228build002; unchanged refusal predicates and pusher.
Request metadata is published by release state1 and consumed with acquire.
Worker final states3/4/6 are release-published after tuple stores and terminal
claim7. Reports acquire state before reading that tuple. Timeout5 deliberately
exposes no worker tuple because a late worker may still be writing it. Request
words remain immutable after release1. No resets, reuse or ownership grant.

Two real ten-word snapshots under FIFO lock: request and worker gate. Indices
0GET,1PUT,2DMA_STATE,3PUSH0,4PUSH1,5DMA_PUSH,6PULL0,7STATUS,8SUBROUTINE,
9PGRAPH_FIFO. No register writes, consuming drain or fabricated empty bits.
One stopped dashboard request precedes one unchanged224 Windows CPU workload.
Old20KiB RAMIN and84KiB CPU tail get actual physical before/after reads, with
explicit selected/restored GDB mode verification. No physical-console access.
Existing211 emulator wizard policy inherited explicitly; no null-device policy.
Positive readback, ended frontend/backend references and native copy remain
unqualified. Inherited Ftdisk49 remains a strict failure if observed.
''')
(k/'NEXT.md').write_text('After closed runtime decode exact raw FIFO states, retain all refusal evidence.\nOnly then design finite queued consumption with frozen producer admission.\nNever unhalt live producers, clear errors or grant native ownership.\n')
dest.write_text(json.dumps(dict(parent_inputs=inputs,actual_compiled_model_stub_pins={n:sha(k/'source'/n) for n in ['gdbstub/gdbstub.c','gdbstub/system.c']},physical_access=False,guest_launch=False),indent=2)+'\n')
print('231 fresh harness authored; no build or guest started')
