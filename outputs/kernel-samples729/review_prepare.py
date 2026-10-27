"""Freeze729 after compiled checks and source/reporting review; no console access."""
from pathlib import Path
import json,hashlib,datetime,ast
K=Path(__file__).resolve().parent;P=Path('C:/xwn729/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda name,data:(K/name).write_text(json.dumps(data,indent=2)+'\n',newline='\n')
assert not (K/'review001.json').exists()
for f in K.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
body=(K/'probe.c').read_text();old=(K.parent/'kernel-interaction728/probe.c').read_text().replace('728','729')
normalized=body.replace(' for(unsigned i=0;i<32;++i)o->blank630[i]=o->blank1b[i]=0xffffffff;\n o->gate630=o->gate1b=o->gate_seq=0xffffffff;\n','')
start=normalized.index(' /* Observe bounded pairs');end=normalized.index(' sw((uint8_t)o->seq_before);',start)
normalized=normalized[:start]+'restore_output:\n gate(4);'+normalized[end+1:]
assert normalized==old,'Only bounded sampling additions allowed'
assert not any(s in body for s in ['Sleep(', 'malloc(', 'Hal', 'Nt', 'CreateFile', 'XVideo'])
assert body.count('cw(0x1b,5)')==1 and 'cw(0x1b,0x85)' not in body
main=(K/'main.c').read_text()
assert 'words[125]' in main and 'i<125' in main and '_Static_assert(sizeof(result)==sizeof(words)' in main
assert main.index('probe729(&result)')<main.index('kernel_sample_words')<main.index('checkpoint("write_control_returned"')<main.index('Sleep(15000)')
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','value.Length == strlen(target)','Partition1','0x7295)?0xff8000','recorded?0xff00ff','XVideoSetMode(1280,720,32,60)']:assert s in main
for name in ['main.c','probe.c','probe.h','layout.c','layout.h','Makefile']:assert sha(K/name)==sha(P/name)
schema=read(K.parent/'kernel-interaction728/schema001.json')
schema=json.loads(json.dumps(schema).replace('728','729'));schema['words']=125
schema['ranges'].update({'54..85':'32 full630 reads while output still blank','86..117':'corresponding32 fullCR1b reads','118..121':'blank count/changes/min/max; changes/min/max include first after6303 sample','122..124':'full630/CR1b/SEQ1 aftergate4 beforeSEQ1 restore'})
schema['unreached']='Additional arrays and gate fields ffffffff; blank counts/min/max zero if no restore630 path'
save('schema001.json',schema)
save('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'matches728_after_removing_only_new_sampling':True,'data_write_sequence_unchanged':True,'new_report_words':125,'new_blank_pairs':32,'gate_sample_before_SEQ_restore':True,'CPU_writes_or_API_calls_in_critical':False,'full_baseline_check_retained':True,'limits':['Additional reads perturb timing; no physical timing equivalence.','First sampled change after a write does not prove causality.','Simulated behavior names do not establish hardware semantics.','Kernel720p remains established; no native modesetting or Windows.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
for name in checks:assert read(K/name)['passed']
checks+=['schema001.json','lineage001.json']
model=read(K/'model001.json')
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':model['case_count'],'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(c['critical_instructions'] for c in model['cases']),'hardware_proved':False})
save('sources001.json',{f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']})
print('PASS729 source equivalence except added samples, reporting and frozen manifest')
