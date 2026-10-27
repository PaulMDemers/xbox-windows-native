"""Freeze exact740 source and reviewed reporting before any physical staging."""
from pathlib import Path
import ast,datetime,hashlib,json,copy
from audit_logic import validate
K=Path(__file__).resolve().parent;P=Path('C:/xwn740/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
body=(K/'probe.c').read_text();main=(K/'main.c').read_text()
previous=(K.parent/'batch-prefix733/probe.c').read_text().replace('733','740')
actual=body[body.index('#include'):]
old=previous[previous.index('#include'):]
actual=actual.replace('i<3;++i){o->attempted_crtc','i<4;++i){o->attempted_crtc')
actual=actual.replace('  uint32_t expected=i==3?o->crtc_before[i]:cs[i][1];\n  if(value!=expected){o->first_mismatch=11+i;o->expected=expected;', '  if(value!=cs[i][1]){o->first_mismatch=11+i;o->expected=cs[i][1];')
assert actual==old, 'unexpected probe change beyond omission and saved-byte comparison'
old=(K.parent/'batch-prefix733/main.c').read_text().replace('733','740').replace('batch_prefix_control','preserve_prefix_control')
assert main[main.index('#include'):]==old[old.index('#include'):]
assert 'i<3;++i){o->attempted_crtc' in body
assert 'cw(0x1b' not in body and 'cw(0x22' not in body and 'cw(0x33' not in body
assert 'o->crtc_restored[i]!=o->crtc_before[i]' in body
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','Partition1','_Static_assert(sizeof(result)==sizeof(words)','Sleep(15000)']:assert s in main
assert main.index('probe740(&result)')<main.index('kernel_sample_words')<main.index('checkpoint("preserve_prefix_control_returned"')<main.index('Sleep(15000)')
for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
cases=read(K/'model001.json')['cases'];assert len(cases)==56
for case in cases:validate(case['raw_result'])
base=cases[0]['raw_result'];mutations=[]
for name,index,value in [('flags',10,0),('cleanup mask',30,1),('count',7,14),('raw checked value',42,1),('code',0,0x7408),('attempted',2,10),('fourth CRTC write',3,4),('saved CR1b',67,5),('first mismatch',4,0)]:
 v=copy.copy(base);v[index]=value
 try:validate(v)
 except AssertionError:mutations.append(name)
 else:raise AssertionError('schema admitted '+name)
bad=next(c['raw_result'] for c in cases if c['name']=='first-mismatch-14')
v=copy.copy(bad);v[6]^=1
try:validate(v)
except AssertionError:mutations.append('mismatch actual')
else:raise AssertionError('schema admitted mismatch corruption')
save('schema001.json',{'words':76,'ranges':{'0':'aggregate status','1':'forward status retained regardless of cleanup','2..3':'MMIO/CRTC write counts','4..7':'first mismatch zero-based0..14 or FFFFFFFF; expected,observed,checked count','8..10':'entry/critical/restored EFLAGS','11..13':'actual critical CR0/3/4','14..16':'saved CRTC/sequencer/graphics selectors','17..18':'SEQ1 before/after','19..20':'CR11 before/after','21..22':'GR04 before/after','23..24':'CR22 before/after','25..26':'CR33 before/after','27':'unlock read informational','28..30':'selectors restored,cleanup_ok,cleanup mismatch bitmask','31..41':'11 MMIO saved','42..52':'11 MMIO checked','53..63':'11 MMIO after recovery','64..67':'four CRTC saved','68..71':'four CRTC checked','72..75':'four CRTC after recovery'},'status':{'740':'forward prefix and full-byte cleanup match','7401':'CPU refusal','7402':'baseline refusal','7403':'blank check rejection','7404':'unlock/context rejection','7408':'forward deferred check rejection','7405':'cleanup mismatch; forward_status still authoritative','7406':'selector mismatch; forward_status still authoritative'},'cleanup_bits':{'0..10':'MMIO','11..14':'CR14,17,19,1b','15..19':'SEQ1,CR11,GR04,CR22,CR33'},'scope':'Kernel-context11 MMIO and3 CRTC writes,15 full-value checks; CR1b compared with actual saved85; no CR1b/CR22/CR33 data writes, native handoff or full-mode replay'})
save('source-review001.json',{'passed':True,'source_only':True,'probe_exact733_except_namespace_header_CR1b_write_omission_and_saved_byte_comparison':True,'main_exact733_except_namespace_header_phase_name':True,'CR1b_CR22_CR33_data_writes':False,'deferred_readback_no_interleaved_reads':True,'cleanup_sequence':'CR19 saved;680630 saved;gate4;SEQ1 saved. Full-byte comparisons unchanged.','independent_schema_cases':56,'rejected_schema_mutations':mutations,'prior_evidence':{n:sha(K.parent/n) for n in ['batch-prefix733/audit001.json','native-batch738/audit001.json','register-contract739/audit001.json']},'limits':['Distinct preservation control, not a relaxed704 predicate or a repaired driver.','CPU context is kernel; native handoff not tested.','Omitting CR1b changes scheduling; no claim about bit7 semantics.','CR22/CR33 programming contracts remain unresolved; their values are only preserved.','Counterfactual execution models cannot prove physical register behavior.','No geometry/encoder/full-mode replay or Windows qualification.','Unused fourth cs entry value5 is retained for exact lineage; index3 uses actual saved byte and is never written.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
assert all(read(K/n)['passed'] for n in checks)
checks+=['schema001.json','lineage001.json']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':56,'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(c['critical_instructions'] for c in cases),'hardware_proved':False})
save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
print('PASS740 schema, negative mutations, source/scope/restore/reporting review and freeze')
