"""Freeze817 exact qualified sources, CPU/layout tests and binary pins."""
from pathlib import Path
import json,hashlib,datetime,ast
K=Path(__file__).resolve().parent;P=Path('C:/xwn817')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
def write(n,v):
 with (K/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
checks=['source-review001.json','schema-review001.json','controller-review001.json','tail003.json','prefix002.json','integration001.json','optical-review001.json','payload008.json','host007.json','host-plan006.json','cpu-build006.json','cpu-run006.json','build002.json','page-review002.json','page-boundary001.json','plan-review001.json','linked-review001.json','link-review012.json']
for n in checks:assert read(n)['passed'],n
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for receipt,folder in [('payload008.json','payload008'),('host007.json','host007'),('build002.json','build002')]:
 b=read(receipt)
 for n,v in b['files'].items():assert sha(P/folder/n)==(v['sha256'] if isinstance(v,dict) else v),n
 for n,v in b.get('sources',{}).items():assert sha(K/n)==v,n
c=read('cpu-run006.json');assert c['closed'] and len(c['cases'])==12 and all(x['closed'] and x['passed'] for x in c['cases'])
assert len(read('host007.json')['relocations'])==53
assert read('payload008.json')['unpadded_bytes']==24744
assert len(read('tail003.json')['cases'])==146 and len(read('prefix002.json')['cases'])==1014
assert len(read('integration001.json')['cases'])==54
assert len(read('schema-review001.json')['rejected_mutations'])==823
assert not read('tail002.json')['passed']
s=read('source-review001.json');assert len(s['all_mask_indices'])==34 and len(s['omitted_aggregate_masks'])==27
schema={'passed':True,'signature':'0x8170000d','names':['signature','final_code','prefix_cleanup_mask','h_cleanup_mask','c4_cleanup_mask','vblank_low_cleanup_mask','linecompare_high_cleanup_mask','cl18_cleanup_mask','mode_controls_cleanup_mask','mode_controls_forward_mask','CR1A_before','CR1A_after','CR1A_after_CR2D_undo_before_own_undo'],'word_indices':s['report_word_indices'],'total_masks_required_for_success':34,'displayed_cleanup_masks':s['displayed_cleanup_masks'],'displayed_forward_mask':916,'omitted_aggregate_masks':s['omitted_aggregate_masks'],'expected_success_rows':[0x8170000d,0x817]+[0]*8+[56,60,60],'limits':['Seven displayed cleanup masks and one forward mask;27 additional cleanup masks aggregate-only','Last raw value is interim CR1A after CR2D undo, not final own restoration','Final CR1A restoration is aggregate-only through cleanup mask and final status','CR25/28/2D same-value controls do not prove an effective write','Kernel preparation is not native evidence']}
write('optical-schema001.json',schema);checks+=['optical-schema001.json']
write('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_words':917,'result_end':0x8654,'allocation_bytes':40960,'payload_bytes':24744,'payload_reserve':28352,'IDT_start':0x8700,'stack_bytes':4352,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':54,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'physical_prerequisite':'CLOSED kernel816 PASS exact917-word result checked by controller','limits':schema['limits']+['No combined visible mode or Windows desktop proof','Selected relocated integration54; full compiled prefix1014 and tail146 checked separately','Historical labels in inherited checker descriptions do not change pinned executable identities']})
write('sources001.json',{'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.S','.py','.ld'] or p.name in ['Makefile','.gitattributes']},'active_payload':'payload_build008.py:probe-pairs-native.c','active_host':'host_build009.py:host007','active_build':'build015.py:build002','active_controller':'physical009.py','active_integration':'integration001.py','active_schema':'audit_logic.py/prefix_audit.py/prefix_schema.py/schema_review001.py','historical_generators_not_to_rerun':True})
print('PASS817 frozen; kernel816 prerequisite enforced; no physical access')
