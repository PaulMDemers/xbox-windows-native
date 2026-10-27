"""Freeze new728 source after compiled tests; no console action."""
import datetime,hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn728/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
native=(K.parent/'native-interaction727/probe.c').read_text().replace('727','728')
old='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200)'
assert native.count(old)==1
assert native.replace(old,'(o->cr0&0x80000001)!=0x80000001')==(K/'probe.c').read_text()
assert (K.parent/'native-interaction727/probe.h').read_text().replace('727','728')==(K/'probe.h').read_text()
body=(K/'probe.c').read_text();main=(K/'main.c').read_text()
assert not any(s in body for s in ['Sleep(', 'malloc(', 'Hal', 'Nt', 'CreateFile', 'XVideo'])
assert body.count('cw(0x1b,5)')==1 and 'cw(0x1b,0x85)' not in body
assert 'words[54]' in main and 'i<54' in main and '_Static_assert(sizeof(result)==sizeof(words)' in main
assert main.index('probe728(&result)')<main.index('kernel_interaction_words')<main.index('checkpoint("write_control_returned"')<main.index('Sleep(15000)')
assert 'CREATE_NEW' in main and 'NtFlushBuffersFile' in main and '!memcmp(report, verify, used)' in main
assert 'value.Length == strlen(target)' in main and 'Partition1' in main
assert '0x7285)?0xff8000' in main and 'recorded?0xff00ff' in main
assert 'XVideoSetMode(1280,720,32,60)' in main
for n in ['main.c','probe.c','probe.h','layout.c','layout.h','Makefile']:assert sha(K/n)==sha(P/n)
schema={'words':54,'ranges':{'0':'code','1':'630 attempts','2..4':'entry/critical/restored EFLAGS','5..7':'actual CR0/CR3/CR4','8..9':'saved selectors','10..11':'SEQ1 before/after','12..14':'before CR11/22/19','15..17':'after CR11/22/19','18':'full baseline cleanup','19':'selector restoration','20..25':'full630 at six stages','26..31':'fullCR1b at six stages','32..37':'packed stage pairs','38..41':'late count/changes/min/max','42':'summary','43..46':'CR1b attempts/unlock attempts/read/CR11','47..49':'prewrite630/CR1b/packed','50..52':'direct/reselected/packed CR1b','53':'packed attempts'},'stages':['baseline','blank','6302','saved6303','output restored','last of32 late pairs'],'codes':{'728':'direct/indexed05 and full baseline restored','7281':'CPU guard','7282':'baseline guard','7283':'blank guard','7285':'full baseline cleanup failed','7286':'selectors failed','7288':'630 or direct/indexed mismatch','7289':'prewrite guard'},'visible':{'green':'728','orange':'7285 or7288','red':'other guard/failure','magenta':'post-call report persistence failed'},'expected_reports':7}
save('schema001.json',schema)
save('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'probe_body_equal_to727_except_namespace_and_CPU_admission':True,'raw_struct_equal':True,'report_words':54,'bounded_no_API_critical_sequence':True,'control_register_writes':False,'no_CR1b_repair_or_mask':True,'native_final85_expectation_retained':True,'limits':['Different compiler and kernel context can change timing; source equivalence is not instruction/timing identity.','Mode remains kernel-established720p; no native modesetting or Windows.','Full saved85 check remains even if kernel retains05. No expected failure waiver.','Automatic firmware return is not normal Windows shutdown.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
for name in checks:assert read(K/name)['passed']
checks+=['schema001.json','lineage001.json','preparation-failure001.json']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':read(K/'model001.json')['case_count'],'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(v['critical_instructions'] for v in read(K/'model001.json')['cases']),'hardware_proved':False})
sources={f.name:sha(f) for f in K.iterdir() if f.suffix in ['.c','.h','.py'] or f.name in ['Makefile','.gitattributes']}
save('sources001.json',sources)
print('PASS728 source equivalence, reporting review and frozen manifest')
