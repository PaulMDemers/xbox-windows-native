"""Independent source scope, raw-schema and exact linked build checks."""
from pathlib import Path
import hashlib,json,datetime,ast,re
from audit_logic import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn775/build001');O=K.parent/'vertical-total773'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['build001.json','model001.json','layout-model001.json','clock-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json']
for n in checks:assert read(n)['passed'],n
for n in ['main.c','probe.c','probe.h','layout.c','layout.h','Makefile']:assert sha(K/n)==sha(P/n)
for n,v in read('build001.json')['files'].items():assert sha(P/n)==v['sha256'],n
for p in K.glob('*.py'):ast.parse(p.read_text())
body=(K/'probe.c').read_text()
assert not re.search(r'R32\([^)]*\)\s*=(?!=)',body)
assert all(n not in body for n in ['cli','sti','outb','outl','wrmsr','popfl','R8(','cw(','sw(','gate('])
assert '0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818' in body
expected=(O/'main.c').read_text().replace('773','775').replace('Kernel775 seven horizontal timing writes, recover before output-enable; no native handoff.','Kernel775 read-only vertical register snapshot; no native handoff.').replace('vertical_total_control','vertical_read_control').replace('words[280]','words[30]').replace('i<280','i<30')
a=expected.index('    /* Never draw or flush');z=expected.index('    uint32_t *pixels=fb;',a)
expected=expected[:a]+'    uint32_t color=recorded?0xff00ff:result.code==0x775?0x00ff00:0xff8000;\n'+expected[z:]
assert expected==(K/'main.c').read_text()
for n in ['layout.c','layout.h']:assert (K/n).read_bytes()==(O/n).read_bytes()
cases=read('model001.json')['cases'];assert len(cases)==49
for c in cases:
 validate(c['raw_result']);assert c['no_MMIO_port_or_CPU_state_writes'] and c['result_and_stack_guards_exact']
v=cases[0]['raw_result'];mutations=0
for i in list(range(4))+list(range(9,30)):
 w=v.copy();w[i]^=1
 try:validate(w)
 except AssertionError:mutations+=1
 else:raise AssertionError(('schema admitted inconsistent mutation',i))
assert mutations==25
legacy=K.parent/'xcal-transaction704/gpu_legacy.c';assert sha(legacy)=='5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690'
assert '// NVVCRTC' in legacy.read_text() and '// NVVVALIDSTART' in legacy.read_text()
review={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'checks':{n:sha(K/n) for n in checks},'probe_read_only':True,'interrupt_state_not_modified':True,'MMIO_reads':21,'result_words':30,'model_cases':49,'schema_mutations_rejected':mutations,'frontend_changes':'namespace,30word result, phases and status rendering; prior timing probe removed','legacy_source_sha256':sha(legacy),'limits':['SDK720p setup and context selector reads still occur in frontend','No custom timing/selector/interrupt writes in probe','Three agreeing reads do not prove atomicity or hardware write semantics']}
for n,r in [('review001.json',review),('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h'] or p.name in ['Makefile','.gitattributes']})]:
 with (K/n).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('PASS775 source and schema review; frozen sources')
