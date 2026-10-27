"""Independent735 schema, exact734 delta, modeled device trace and source freeze."""
from pathlib import Path
import ast,datetime,hashlib,json,copy
from audit_logic import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn735/build001');old=K.parent/'cr1b-read734'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
body=(K/'probe.c').read_text();start=body.index(' o->direct[0]=');end=body.index(' o->after_direct630=',start)
interval=body[start:end]
assert 'roll $1,%0; xorl $0x9e3779b9,%0; decl %1; jnz 1b' in interval
assert 'uint32_t count=4093,sum=0x13579bdf' in interval
assert not any(t in interval for t in ['cw(','sw(','gate(','R32(','cr(','rdtsc','inb','outb'])
assert body[:start]+' for(unsigned n=0;n<16;++n){o->direct[n]=R8(0x6013d5);o->direct_count=n+1;}\n'+body[end:]==(old/'probe.c').read_text().replace('734','735')
assert (K/'probe.h').read_text().replace(' uint32_t cpu_iterations,cpu_counter_end,cpu_checksum;\n','')==(old/'probe.h').read_text().replace('734','735')
main=(K/'main.c').read_text()
assert main==(old/'main.c').read_text().replace('734','735').replace('cr1b_read_control','cr1b_work_control').replace('words[112]','words[115]').replace('i<112','i<115').replace('CR1b read blocks before prefix cleanup735','CR1b read blocks with bounded CPU work735')
for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','_Static_assert(sizeof(result)==sizeof(words)','Sleep(15000)']:assert s in main
cases=read(K/'model001.json')['cases'];assert len(cases)==60
for c in cases:validate(c['raw_result'])
base=cases[0]['raw_result'];mutations=[]
for name,index,value in [('flags',10,0),('cleanup',30,1),('count',7,14),('value',42,1),('code',0,0x7358),('attempted',2,10),('first',4,0),('direct count',76,15),('indexed count',77,17),('sample width',80,256),('missing sample',111,0xffffffff),('iterations',112,4092),('counter end',113,1),('checksum',114,0)]:
 v=copy.copy(base);v[index]=value
 try:validate(v)
 except AssertionError:mutations.append(name)
 else:raise AssertionError('schema admitted '+name)
for c in cases:
 if c['raw_result'][3]!=4:continue
 reads=[x for x in c['reads'] if x[3]==0x7354 and not x[4]][2:]
 assert [x[0] for x in reads]==[0x6013d5]*16+[0x680630]+[0x6013d5]*16+[0x680630]
 assert c['writes']==cases[0]['writes']
schema=read(old/'schema001.json');schema['words']=115;schema['ranges']['112..114']='CPU-work iteration count4093, terminal counter0, rotate/xor checksum'
schema['status']={k.replace('734','735'):v for k,v in schema['status'].items()};schema['scope']='734 plus bounded register-only work after direct sample1; no new device write or predicate change'
save('schema001.json',schema)
save('source-review001.json',{'passed':True,'probe_exact734_plus_cpu_work':True,'reporting_only_main_delta':True,'schema_cases':60,'schema_mutations_rejected':mutations,'same_qualified_device_write_sequence':True,'same_device_read_address_sequence_as734':True,'actual_loop_checksum_validated':True,'limits':['Intervening work is not calibrated elapsed time.','CPU/kernel context and read schedule differ from native full-mode replay.','NV3 underflow label is a cross-generation hypothesis, not NV2A bit7 specification.','No guessed writable mask or validation waiver.','Automatic dashboard return inferred from durable restart-request report and reachability; screen color is unobserved.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
assert all(read(K/n)['passed'] for n in checks)
checks+=['schema001.json','lineage001.json']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':60,'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(c['critical_instructions'] for c in cases),'physical_semantics_proved':False})
save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
print('PASS735 source/schema/read-write trace review; frozen')
