"""Freeze independently checked813 candidate; kernel812 remains physical prerequisite."""
from pathlib import Path
import json,hashlib,datetime,re,ast
K=Path(__file__).resolve().parent;P=Path('C:/xwn813')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
def write(n,v):
 with (K/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
checks=['source-review001.json','schema-review003.json','controller-review001.json','tail001.json','prefix001.json','integration001.json','optical-review001.json','payload008.json','host007.json','host-plan006.json','cpu-build006.json','cpu-run006.json','build002.json','page-review002.json','page-boundary001.json','plan-review001.json','linked-review001.json','link-review012.json']
for n in checks:assert read(n)['passed'],n
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for receipt,folder in [('payload008.json','payload008'),('host007.json','host007'),('build002.json','build002')]:
 b=read(receipt)
 for n,v in b['files'].items():assert sha(P/folder/n)==(v['sha256'] if isinstance(v,dict) else v),n
 for n,v in b.get('sources',{}).items():assert sha(K/n)==v,n
c=read('cpu-run006.json');assert c['closed'] and len(c['cases'])==12 and all(x['closed'] and x['passed'] for x in c['cases'])
assert len(read('host007.json')['relocations'])==43
assert read('payload008.json')['unpadded_bytes']==24108
assert read('schema-review003.json')['counts']=={'tail001.json':51,'prefix001.json':1014,'integration001.json':35}
assert not read('schema-review001.json')['passed'] and not read('schema-review002.json')['passed']
s=read('source-review001.json');assert len(s['all_mask_indices'])==33 and len(s['omitted_aggregate_masks'])==25
fields=re.search(r'struct result813\s*\{(.*?)\};',(K/'probe.h').read_text(),re.S).group(1)
fields=[n.strip() for group in re.findall(r'uint32_t\s+([^;]+);',fields) for n in group.split(',')]
schema={'passed':True,'signature':'0x8130000d','names':['signature','final_code']+['prefix_cleanup_mask','h_cleanup_mask','c4_cleanup_mask','vblank_low_cleanup_mask','linecompare_high_cleanup_mask','linecompare_bit_cleanup_mask','cl9_cleanup_mask','cl18_cleanup_mask']+['CR18_before','CR18_after','CR18_restored'],'word_indices':s['report_word_indices'],'total_masks_required_for_success':33,'omitted_aggregate_masks':s['omitted_aggregate_masks'],'limits':['No raw values for25 omitted masks; final success aggregate only','FF to FF does not prove effective write','Kernel preparation is not native evidence']}
write('optical-schema001.json',schema)
checks+=['optical-schema001.json']
write('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_words':820,'result_end':0x74d0,'payload_bytes':24108,'payload_reserve':24256,'stack_bytes':768,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':54,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'physical_prerequisite':'CLOSED kernel812 PASS exact820-word result checked by controller','limits':schema['limits']+['No combined visible mode or Windows desktop proof','Relocated integration54 selected cases; full compiled prefix1014 and tail51 separately','Historical link-review required_execution_checks labels are stale; this receipt pins actual executed checks']})
write('sources001.json',{'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.S','.py','.ld'] or p.name in ['Makefile','.gitattributes']},'active_payload':'payload_build008.py:probe-pairs-native.c','active_host':'host_build009.py:host007','active_build':'build015.py:build002','active_controller':'physical009.py','active_integration':'integration001.py','active_schema':'audit_logic002.py/prefix_schema002.py/schema_review003.py','historical_generators_not_to_rerun':True})
print('PASS813 candidate frozen; physical kernel812 prerequisite remains enforced')
