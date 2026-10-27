"""Freeze exact733 source and reviewed reporting before any physical staging."""
from pathlib import Path
import ast,datetime,hashlib,json,copy
from audit_logic import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn733/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
body=(K/'probe.c').read_text();main=(K/'main.c').read_text()
previous=(K.parent/'kernel-prefix723/probe.c').read_text()
for label,end in [('static const uint32_t setup','static uint8_t cr')]:
 a=body[body.index(label):body.index(end)]
 b=previous[previous.index(label):previous.index(end)]
 assert a==b
batch=body[body.index(' for(unsigned i=0;i<11;++i){o->attempted_mmio'):body.index(' o->forward_status=0x7338;')]
assert 'R32(setup[i][0])=setup[i][1]' in batch and 'cw(cs[i][0],cs[i][1])' in batch
assert 'cr(' not in batch and 'mmio_checked' not in batch
assert 'cw(0x22' not in body and 'cw(0x33' not in body and 'cw(0x1b' not in body
assert 'R8(0xc03cf)=' not in body and '0x80d3' in body
assert 'o->crtc_restored[i]!=o->crtc_before[i]' in body
old=(K.parent/'latch-select731/main.c').read_text().replace('731','733').replace('words[43]','words[76]').replace('i<43','i<76').replace('read_plane_control','batch_prefix_control').replace('result.code==0x7333 || result.code==0x7335','result.code==0x7338 || result.code==0x7335')
assert main==old
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','Partition1','_Static_assert(sizeof(result)==sizeof(words)','Sleep(15000)']:assert s in main
assert main.index('probe733(&result)')<main.index('kernel_sample_words')<main.index('checkpoint("batch_prefix_control_returned"')<main.index('Sleep(15000)')
for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
cases=read(K/'model001.json')['cases'];assert len(cases)==55
for case in cases:validate(case['raw_result'])
base=cases[0]['raw_result'];mutations=[]
for name,index,value in [('flags',10,0),('cleanup mask',30,1),('count',7,14),('raw checked value',42,1),('code',0,0x7338),('attempted',2,10),('first mismatch',4,0)]:
 v=copy.copy(base);v[index]=value
 try:validate(v)
 except AssertionError:mutations.append(name)
 else:raise AssertionError('schema admitted '+name)
bad=next(c['raw_result'] for c in cases if c['name']=='first-mismatch-14')
v=copy.copy(bad);v[6]^=1
try:validate(v)
except AssertionError:mutations.append('mismatch actual')
else:raise AssertionError('schema admitted mismatch corruption')
save('schema001.json',{'words':76,'ranges':{'0':'aggregate status','1':'forward status retained regardless of cleanup','2..3':'MMIO/CRTC write counts','4..7':'first mismatch zero-based0..14 or FFFFFFFF; expected,observed,checked count','8..10':'entry/critical/restored EFLAGS','11..13':'actual critical CR0/3/4','14..16':'saved CRTC/sequencer/graphics selectors','17..18':'SEQ1 before/after','19..20':'CR11 before/after','21..22':'GR04 before/after','23..24':'CR22 before/after','25..26':'CR33 before/after','27':'unlock read informational','28..30':'selectors restored,cleanup_ok,cleanup mismatch bitmask','31..41':'11 MMIO saved','42..52':'11 MMIO checked','53..63':'11 MMIO after recovery','64..67':'four CRTC saved','68..71':'four CRTC checked','72..75':'four CRTC after recovery'},'status':{'733':'forward prefix and full-byte cleanup match','7331':'CPU refusal','7332':'baseline refusal','7333':'blank check rejection','7334':'unlock/context rejection','7338':'forward deferred check rejection','7335':'cleanup mismatch; forward_status still authoritative','7336':'selector mismatch; forward_status still authoritative'},'cleanup_bits':{'0..10':'MMIO','11..14':'CR14,17,19,1b','15..19':'SEQ1,CR11,GR04,CR22,CR33'},'scope':'Kernel-context15-entry prefix; no CR22/CR33 data writes, native handoff or full-mode replay'})
save('source-review001.json',{'passed':True,'source_only':True,'prefix_arrays_equal723':True,'main_scaffold_only_reporting_changes':True,'deferred_readback_no_interleaved_reads':True,'cleanup_sequence':'CR19 saved;680630 saved;gate4;SEQ1 saved. No CR1b or CR22 restore write. Full-byte before/after mismatches retained.','independent_schema_cases':55,'rejected_schema_mutations':mutations,'prior_evidence':{n:sha(K.parent/n) for n in ['kernel-prefix723/audit001.json','native-prefix725/REPORT.md','latch-select731/audit001.json','latch-model732/audit001.json']},'limits':['Compared prefix omits CR22/CR33 writes; not exact replay of original full setup.','CPU context is kernel, not native flat context.','Added instrumentation and changed check scheduling alter timing.','CR1b05 may remain after the single write; cleanup reports mismatch without attempting85.','No CR22/CR33 programming contract established; no full-recipe admission.','Inherited main.c header comment names the731 source experiment; actual733 behavior is defined by probe.c and this reviewed schema.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
assert all(read(K/n)['passed'] for n in checks)
checks+=['schema001.json','lineage001.json']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':55,'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(c['critical_instructions'] for c in cases),'hardware_proved':False})
save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
print('PASS733 schema, negative mutations, source/scope/restore/reporting review and freeze')
