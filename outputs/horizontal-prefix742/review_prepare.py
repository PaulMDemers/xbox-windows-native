"""Pin742 source, independent target derivation, recovery and result contracts."""
import ast,datetime,hashlib,json,re,struct
from pathlib import Path
from audit_logic import validate,BASELINE,TARGET
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn742/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
pins={
 'outputs/xcal-transaction704/gpu_legacy.c':'5e686c6e875f9d9bb60a0955bedfb4978911f5a79bf1feaea47080d9d7fe5690',
 'outputs/xcal-transaction704/gpu_types.h':'1f7c61fa6599b4242f623f91ac849e47786ad726e9656a03b9fad6652b6198e9'}
for p,h in pins.items():assert sha(W/p)==h
assert sha(Path('C:/xwn700/source001/BootVgaInitialization.c'))=='481e95c8335ba0d865b3ccddfc1b1acfaf0721e12045104e37c5d4d13573c4d4'
assert sha(Path('C:/xwn702/source001/envytools-nv3_pramdac.xml'))=='5ce70338362d0c55221c11fad266147818afe1bc97ef971eb2493ef5d84ea3cd'
legacy=(W/'outputs/xcal-transaction704/gpu_legacy.c').read_text()
portion=legacy[legacy.index('void SetGPURegister'):legacy.index('// CRTC_HSYNCSTART')]
pairs=re.findall(r'pbRegs\[(0x[0-9a-f]+)\]\) = ([^;]+);',portion)
assert len(pairs)==7
addresses=[int(a,16) for a,_ in pairs]
assert addresses==[0x680820,0x680824,0x680828,0x680834,0x68082c,0x680830,0x680838]
params={'crtchdispend':720,'nvhtotal':779,'xres':720,'nvhstart':738}
values=[]
for _,expr in pairs:
 for field,value in params.items():expr=expr.replace('gpu->'+field,str(value))
 assert re.fullmatch(r'[0-9 +\-]+',expr)
 values.append(eval(expr,{'__builtins__':{}},{}))
assert values==TARGET
assert 'target={720,720,738,779,480,489,489,524,524,4,3}' in (W/'outputs/xcal-transaction704/transaction003.c').read_text()
captures=read(W/'outputs/kernel-mode722/collection001.json')['reports']
baseline_captures=[]
for name,row in captures.items():
 d=row['data']
 if d['phase']=='mode_captured' and d['stage'] in [0,2]:
  assert [dict(d['mmio'])[a] for a in addresses]==BASELINE
  baseline_captures.append(name)
assert len(baseline_captures)==2
body=(K/'probe.c').read_text();main=(K/'main.c').read_text()
old=(W/'outputs/preserve-prefix740/probe.c').read_text().replace('740','742')
for a,z in [('static const uint32_t setup','/* First seven'),('static const uint8_t cs','void probe742')]:
 source_part=body[body.index(a):body.index(z)]
 if a.startswith('static const uint32_t'):assert source_part.strip()==old[old.index(a):old.index('static const uint8_t cs')].strip()
 else:assert source_part==old[old.index(a):old.index(z)]
assert body[body.index(' sw(0x21)'):body.index(' /* Only proceed')]==old[old.index(' sw(0x21)'):old.index(' o->forward_status=0x742;')]
assert 'R32(horizontal[i-1][0])=o->h_before[i-1]' in body
assert body.index('o->h_restored[i]!=o->h_before[i]')<body.index('if(!o->h_cleanup_mask){gate(4)')
assert 'cw(0x1b' not in body and 'cw(0x22' not in body and 'cw(0x33' not in body
for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
for n in ['layout.c','layout.h']:assert (K/n).read_text()==(W/'outputs/preserve-prefix740'/n).read_text()
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','Partition1','_Static_assert(sizeof(result)==sizeof(words)','Sleep(15000)']:assert s in main
assert main.index('probe742(&result)')<main.index('kernel_sample_words')<main.index('checkpoint("horizontal_prefix_control_returned"')<main.index('if(result.h_cleanup_mask)')<main.index('uint32_t *pixels=fb;')
table=struct.pack('<21I',*[n for a,t,b in zip(addresses,TARGET,BASELINE) for n in [a,t,b]])
for n in ['main.exe','bin/default.xbe']:assert (P/n).read_bytes().count(table)==1
cases=read(K/'model001.json')['cases'];assert len(cases)==89
for case in cases:validate(case['raw_result'])
base=cases[0]['raw_result'];mutations=[]
for index,value in [(0,0x7429),(1,0x7428),(2,10),(3,4),(4,0),(7,14),(10,0),(30,1),(42,1),(67,5),(76,0),(83,0),(90,0),(97,6),(98,6),(99,0),(100,1),(101,0),(102,1),(103,1)]:
 v=base.copy();v[index]=value
 try:validate(v)
 except AssertionError:mutations.append(index)
 else:raise AssertionError('admitted result mutation '+str(index))
bad=next(c['raw_result'] for c in cases if c['name']=='horizontal-recovery-read-0')
v=bad.copy();v[101]=1
try:validate(v)
except AssertionError:mutations.append('enable-after-failed-restore')
else:raise AssertionError('admitted enabled output with restore mismatch')
schema={'words':104,'prefix_words':'0..75 identical740 layout; statuses renamed742','horizontal_before':'76..82','horizontal_checked':'83..89','horizontal_restored':'90..96','attempted':97,'checked_count':98,'first_mismatch':99,'cleanup_mask':100,'output_enable_attempted':101,'expected':102,'observed':103,'new_statuses':{'7429':'horizontal forward mismatch','742a':'horizontal recovery mismatch; leave blank'},'scope':'kernel-only horizontal checkpoint; no visible low-resolution output or native/Windows proof'}
save('schema001.json',schema)
save('source-review001.json',{'passed':True,'pins':pins,'baseline_captures':baseline_captures,'addresses':addresses,'targets':TARGET,'baseline':BASELINE,'same_run_restore_only':True,'no_output_enable_after_horizontal_restore_mismatch':True,'linked_horizontal_table_exact':True,'prefix_forward_exact740':True,'independent_schema_cases':len(cases),'rejected_mutations':mutations,'scope_document_sha256':sha(K/'SOURCE-REVIEW.md'),'retained_evidence':{n:sha(W/n) for n in ['outputs/kernel-mode722/collection001.json','outputs/preserve-prefix740/audit001.json','outputs/native-preserve741/audit001.json','outputs/xcal-transaction704/transaction003.c']}})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
assert all(read(K/n)['passed'] for n in checks)
checks+=['schema001.json','lineage001.json','SOURCE-REVIEW.md']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':89,'layout_cases':2353,'max_modeled_critical_instructions':max(c['critical_instructions'] for c in cases),'hardware_proved':False})
save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
print('PASS742 independent derivation, schema, access/restore review and exact-source freeze')
