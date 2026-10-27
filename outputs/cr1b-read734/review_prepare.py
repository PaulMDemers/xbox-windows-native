"""Freeze734 after checking its exact difference from733 and independent schema."""
from pathlib import Path
import ast,datetime,hashlib,json,copy
from audit_logic import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn734/build001');old=K.parent/'batch-prefix733'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
body=(K/'probe.c').read_text();previous=(old/'probe.c').read_text().replace('733','734')
start=body.index(' /* The last write selected CR1b.')
end=body.index(' o->forward_status=0x7348;',start)
samples=body[start:end]
assert samples.count('R8(0x6013d5)')==1 and samples.count('cr(0x1b)')==1
assert samples.count('R32(0x680630)')==2 and samples.count('n<16')==2
assert not any(t in samples for t in ['cw(','sw(','gate(','=5','while('])
reduced=body[:start]+body[end:]
reduced=reduced.replace(' * Batch all writes, sample CR1b before cleanup, then retain original checks.\n * Two ordered read blocks are observations, not a timing or selector-cause proof.', ' * Batch all writes, then check in original order. No interleaved readback.')
reduced=reduced.replace(' o->after_direct630=o->after_indexed630=0xffffffff;\n for(unsigned i=0;i<16;++i)o->direct[i]=o->indexed[i]=0xffffffff;\n','')
assert reduced==previous,'Unexpected change outside appended observations'
header=(K/'probe.h').read_text().replace(' uint32_t direct_count,indexed_count,after_direct630,after_indexed630;\n uint32_t direct[16],indexed[16];\n','')
assert header==(old/'probe.h').read_text().replace('733','734')
main=(K/'main.c').read_text()
expected=(old/'main.c').read_text().replace('733','734').replace('words[76]','words[112]').replace('i<76','i<112').replace('batch_prefix_control','cr1b_read_control').replace('Kernel-context CR22 observations under bounded GR04 selection734.','Kernel-context CR1b read blocks before prefix cleanup734.')
assert main==expected
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','Partition1','_Static_assert(sizeof(result)==sizeof(words)','Sleep(15000)']:assert s in main
assert main.index('probe734(&result)')<main.index('kernel_sample_words')<main.index('checkpoint("cr1b_read_control_returned"')<main.index('Sleep(15000)')
for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
cases=read(K/'model001.json')['cases'];assert len(cases)==59
for case in cases:validate(case['raw_result'])
base=cases[0]['raw_result'];mutations=[]
for name,index,value in [('flags',10,0),('cleanup mask',30,1),('count',7,14),('raw checked value',42,1),('code',0,0x7348),('attempted',2,10),('first mismatch',4,0),('direct count',76,15),('indexed count',77,17),('sample width',80,256),('missing indexed sample',111,0xffffffff)]:
 v=copy.copy(base);v[index]=value
 try:validate(v)
 except AssertionError:mutations.append(name)
 else:raise AssertionError('schema admitted '+name)
bad=next(c['raw_result'] for c in cases if c['name']=='first-mismatch-14')
v=copy.copy(bad);v[6]^=1
try:validate(v)
except AssertionError:mutations.append('mismatch actual')
else:raise AssertionError('schema admitted mismatch corruption')
schema=read(old/'schema001.json');schema['words']=112
schema['ranges'].update({'76..77':'direct/indexed completed counts,16 each after prefix','78..79':'680630 after direct/indexed blocks, raw full width','80..95':'16 direct byte reads with CR1b left selected by write','96..111':'16 byte reads, each explicitly reselecting CR1b'})
schema['status']={k.replace('733','734'):v for k,v in schema['status'].items()}
schema['scope']='733 qualified prefix/data-write/recovery sequence, appended32 CR1b observations before deferred checks; no predicate masking'
save('schema001.json',schema)
save('source-review001.json',{'passed':True,'source_only':True,'probe_exact733_plus_initialization_and_read_blocks':True,'main_only_reporting_and_header_changes':True,'independent_schema_cases':59,'rejected_schema_mutations':mutations,'original_source_sha256':sha(old/'probe.c'),'limits':['Kernel context only, no native handoff or full mode replay.','The ordered blocks alter read scheduling; differences do not isolate elapsed time or selector causality.','No NV2A bit7 semantics or writable mask has been established.','Samples are raw observations and do not override any full-byte deferred/cleanup comparison.','No sample is a timestamp. Host policies are hypothetical, not physical behavior.','Preparation helper was followed by explicit source edits to correct its inherited header and exclude the initial write-selector from model sample counting, before the first build/model run.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
assert all(read(K/n)['passed'] for n in checks)
assert read(K/'references001.json')['completed']
checks+=['schema001.json','lineage001.json','references001.json']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':59,'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(c['critical_instructions'] for c in cases),'hardware_proved':False})
save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
print('PASS734 exact-difference/schema/reporting review; source frozen')
