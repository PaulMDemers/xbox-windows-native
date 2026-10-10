"""Pin the actual compiled PGRAPH wait producer/clearer; static evidence only."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
dest=k/'wait-source001.json';assert not dest.exists()
pins=json.loads((k/'candidate001-source-pins.json').read_text())
name='hw/xbox/nv2a/pgraph/pgraph.c'
data=subprocess.check_output(['wsl','-d','Ubuntu','--','cat','/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/'+name])
digest=hashlib.sha256(data).hexdigest();assert digest==pins[name]
p=k/'artifacts/wait-source001/pgraph.c';p.parent.mkdir();p.write_bytes(data)
text=data.decode();lines=text.splitlines()
sites=[dict(line=i+1,text=line) for i,line in enumerate(lines) if 'waiting_for_nop' in line]
assert len(sites)==2
assert 'pg->pending_interrupts &= ~val;' in text
assert 'if (!(pg->pending_interrupts & NV_PGRAPH_INTR_ERROR))' in text
assert 'DEF_METHOD(NV097, NO_OPERATION)' in text
assert 'if (parameter == 0)' in text
dest.write_text(json.dumps(dict(passed=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    compiled_source=name,compiled_source_sha256=digest,artifact=str(p.relative_to(k)),sites=sites,
    static_producer='Nonzero NV097 NO_OPERATION sets trapped method/data and ERROR interrupt, sets waiting_for_nop, then updates IRQ.',
    static_clearer='Actual guest NV_PGRAPH_INTR write removes supplied pending bits and clears waiting_for_nop only once ERROR is absent, then kicks PFIFO.',
    runtime_proven='consume232 observed waiting_for_nop before/after with zero parser iterations and zero committed words.',
    runtime_not_proven='No trapped method/parameter, interrupt mask, guest acknowledgement write or complete wait lifecycle was captured in this case.',
    physical_access=False,qualification=False),indent=2)+'\n')
print('232 actual compiled PGRAPH wait source pin PASS; lifecycle remains unobserved')
